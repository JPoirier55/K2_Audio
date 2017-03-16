"""
FILE:   tcp_server.py
DESCRIPTION: TCP server module which runs on boot and handles incoming
messages from the DSP through TCP connection.

Can be run through the command line with arguments for HOST (--h) and PORT (--p)
to start the server running locally or through dev env.
Currently only supports IPv4

WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
2/1/17          JDP                original
"""

import json
from message_utils import MessageHandler, error_response, handle_unsolicited
import argparse
import threading
from threading import Lock
import SocketServer
import serial
import select
import Queue
import socket

DEBUG = True
DEV_UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2']
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
SERVER_QUEUE = Queue.Queue()
CLIENT_QUEUE = Queue.Queue()
MIDDLE_QUEUE = Queue.Queue()

uart_lock1 = Lock()
uart_lock2 = Lock()
uart_lock4 = Lock()
uart_lock5 = Lock()

LOCKS = {'/dev/ttyO1': uart_lock1,
         '/dev/ttyO2': uart_lock2,
         '/dev/ttyO4': uart_lock4,
         '/dev/ttyO5': uart_lock5}

MICRO_ACK = bytearray('E8018069EE')
BB_ACK = bytearray('E8018069EE')
DSP_SERVER_IP = '192.168.255.88'
DSP_SERVER_PORT = 8003


class SerialSendHandler:
    def __init__(self, port, baudrate=115200, timeout=None):
        """
        Init baudrate and timeout for serial
        @param baudrate: baudrate, default 115200
        @param timeout: timeout, default None
        """
        self.baudrate = baudrate
        self.timeout = timeout
        self.port = port
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)

    def read_uart(self):
        line = self.ser.readline()
        return line

    def flush_input(self):
        self.ser.flushInput()

    def send_uart(self, command):
        """
        Connect to serial connection and send command.
        Then close serial connection
        @param json_command: Command to be sent to uart
        @param uart_send: port to write command to
        @return: None
        """
        print 'sending: ', command, " ", self.port
        print ":".join("{:02x}".format(c) for c in command)
        self.ser.write(command)

    def close(self):
        self.ser.close()


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def serial_handle(self, uart_command, uart_port):
        """
        Generic method which handles the serial locking
        and conversion to be sent, also checks the recv
        ack from the micro to verify its correct
        @param uart_command: command from micro
        @param uart_port: port command comes on
        @return:
        """
        ack = True
        while True:
            if LOCKS[uart_port].acquire():
                try:
                    ser = SerialSendHandler(uart_port)
                    ser.flush_input()
                    print uart_command
                    command = bytearray.fromhex(uart_command)
                    print command
                    # ser.send_uart(command)
                    # micro_response = ser.read_uart()
                    # TODO: integrate with micro to get ack back for each command
                    # if micro_response == MICRO_ACK:
                    #     ack = True
                    ser.close()
                finally:
                    LOCKS[uart_port].release()
                break
        return ack


    def handle(self):
        """
        TCP Socket Server builtin function to handle
        incoming packets. Inserts messages onto the
        threaded global queue GLOBAL_QUEUE object along
        with the uart port set by the incoming component_id
        @return: None
        """
        self.data = self.request.recv(1024)

        try:
            json_data = json.loads(self.data)
        except Exception as e:
            return None

        if all(key in json_data for key in ("action", "category", "component", "component_id", "value")):
            msg = MessageHandler(json_data)
            response, (uart_command, uart_port) = msg.process_command()
            print 'response:', response
            print 'uart com :', uart_command
            print 'uart port: ', uart_port

            if not uart_port or not uart_command:
                self.request.sendall(json.dumps(response) + '\n')
                return

            elif uart_port == "ALL":
                ack_num = 0
                for uart_port in UART_PORTS:
                    while True:
                        if(self.serial_handle(uart_command, uart_port)):
                            ack_num += 1
                        break
                if ack_num == 4:
                    self.request.sendall(json.dumps(response))

            elif uart_port == "ARRAY":
                ack_num = 0
                count = 0
                for uart_port, single_uart_command in uart_command.iteritems():
                    count += 1
                    if len(single_uart_command) > 0:
                        single_command = json.dumps(single_uart_command).strip('"')
                        if self.serial_handle(single_command, uart_port):
                            ack_num += 1
                if ack_num == count:
                    self.request.sendall(json.dumps(response))

            else:
                if self.serial_handle(uart_command, uart_port):
                    self.request.sendall(json.dumps(response))
        else:
            self.request.sendall(error_response(1)[0] + '\n')


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    Built in for Threaded SocketServer
    """
    pass


class SerialReceiveHandler:

    def __init__(self, baudrate=115200, timeout=None):
        """
        Initialize list of uart ports and setup serial
        listeners for incoming messages
        @param baudrate: baudrate, default 115200
        @param timeout: serial timeout, default None
        """
        self.uarts = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
        self.timeout = timeout
        serial_listeners = self.setup_listeners()
        self.TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_CLIENT.connect((DSP_SERVER_IP, DSP_SERVER_PORT))

        '''
        Possible other functions for threading serial
        connections instead of using Select:

        self.setup_threads(serial_listeners)
        '''

        self.listen_serial(serial_listeners)

    def setup_listeners(self):
        """
        Creates array of serial fd handles for
        each of the uarts on the bb
        @return: array of serial handles
        """
        sers = []
        for uart in self.uarts:
            try:
                ser = serial.Serial(uart, baudrate=115200, timeout=self.timeout)
                sers.append(ser)
            except serial.SerialException as e:
                print 'Serial Exception Thrown on connection: ', e
                continue
        return sers

    def listen_serial(self, sers):
        """
        While loop for incoming serial messages
        to be handed when they are able to be handled.
        Select statement makes this non-blocking reads of
        serial connections
        @param sers: array of serial handlers
        @return: None
        """
        while 1:
            readable, writable, exceptional = select.select(sers, [], sers)
            for serial_connection in readable:
                try:
                    incoming_command = ""
                    if LOCKS[serial_connection.port].acquire():
                        try:
                            while True:
                                var = serial_connection.read(1)
                                if ord(var) == 0xee:
                                    incoming_command += var
                                    if DEBUG:
                                        print ":".join("{:02x}".format(ord(c)) for c in incoming_command)
                                    break
                                else:
                                    incoming_command += var
                                serial_connection.write(BB_ACK)
                        finally:
                            LOCKS[serial_connection.port].release()

                    msg = handle_unsolicited(incoming_command)
                    self.TCP_CLIENT.sendall(json.dumps(msg))

                except serial.SerialException as e:
                    print 'Cannot read line, Serial Exception Thrown:  ', e
                    continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST, PORT = args.h, args.p

    server = ThreadedTCPServer((HOST, int(PORT)), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    print ip, port

    server_thread = threading.Thread(target=server.serve_forever)
    serial_thread = threading.Thread(target=SerialReceiveHandler)

    server_thread.daemon = True
    server_thread.start()
    serial_thread.daemon = True
    serial_thread.start()

    if DEBUG:
        print "Server loop running in thread:", server_thread.name
        print 'Global serial handler running in thread: ', serial_thread.name

    server.serve_forever()
