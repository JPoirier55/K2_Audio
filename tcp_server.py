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
import serial
import select
import Queue
import socket
import time
import sys


DEBUG = True
DEV_UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2']
xUART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO1','/dev/ttyO1','/dev/ttyO1']
SERVER_QUEUE = Queue.Queue()
CLIENT_QUEUE = Queue.Queue()
MIDDLE_QUEUE = Queue.Queue()

uart_lock1 = Lock()
uart_lock2 = Lock()
uart_lock4 = Lock()
uart_lock5 = Lock()

xLOCKS = {'/dev/ttyO1': uart_lock1,
          '/dev/ttyO2': uart_lock2,
          '/dev/ttyO4': uart_lock4,
          '/dev/ttyO5': uart_lock5}

LOCKS = {'/dev/ttyO4': uart_lock1
         }

MICRO_ACK = bytearray('E8018069EE')
BB_ACK = bytearray('E8018069EE')
DSP_SERVER_IP = '192.168.255.88'
DSP_SERVER_PORT = 65000


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


def serial_handle(uart_command, uart_port):
    """
    Generic method which handles the serial locking
    and conversion to be sent, also checks the recv
    ack from the micro to verify its correct
    @param uart_command: command from micro
    @param uart_port: port command comes on
    @return:
    """
    ser = serial.Serial('/dev/ttyO4', 115200)
    command = bytearray.fromhex(uart_command)

    if DEBUG:
        print command, uart_port

    ser.write(command)
    ser.close()
    return True

    '''
    ack = False
    while True:
        if LOCKS[uart_port].acquire():
            try:
                # ser = SerialSendHandler(uart_port)
                # ser.flush_input()
                ser = serial.Serial('/dev/ttyO1', 115200)
                command = bytearray.fromhex(uart_command)

                if DEBUG:
                    print command, uart_port

                ser.write(command)
                micro_response = ""
                while True:
                    var = ser.read(1)
                    if ord(var) == 0xee:
                        micro_response += var
                        # print ":".join("{:02x}".format(ord(c)) for c in micro_response)
                        # TODO: check ack here
                        break
                    else:
                        micro_response += var
                ser.close()
            finally:
                LOCKS[uart_port].release()
            break
    return ack
    '''


class SerialReceiveHandler:

    def __init__(self, baudrate=115200, timeout=None):
        """
        Initialize list of uart ports and setup serial
        listeners for incoming messages
        @param baudrate: baudrate, default 115200
        @param timeout: serial timeout, default None
        """
        self.uarts = UART_PORTS
        self.timeout = timeout
        serial_listeners = self.setup_listeners()
        self.TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_CLIENT.connect((DSP_SERVER_IP, DSP_SERVER_PORT))

        self.listen_serial(serial_listeners)

    def setup_listeners(self):
        """
        Creates array of serial fd handles for
        each of the uarts on the bb
        @return: array of serial handles
        """
        sers = []
        for uart in self.uarts:
            print uart
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
                        # TODO: Check for RTS gpio to see if high
                        try:
                            while True:
                                var = serial_connection.read(1)
                                if ord(var) == 0xee:
                                    incoming_command += var
                                    if DEBUG:
                                        print ":".join("{:02x}".format(ord(c)) for c in incoming_command), serial_connection.port
                                    break
                                else:
                                    incoming_command += var
                                serial_connection.write(BB_ACK)
                        finally:
                            LOCKS[serial_connection.port].release()

                    msg = handle_unsolicited(incoming_command)
                    print msg
                    # self.TCP_CLIENT.sendall(json.dumps(msg))

                except serial.SerialException as e:
                    print 'Cannot read line, Serial Exception Thrown:  ', e
                    continue


class DataHandler:

    def handle_all_msg(self, uart_command):
        """
        Handle messages that go to all uarts
        @param uart_command: 
        @return: 
        """
        ack_num = 0
        for uart_port in UART_PORTS:
            while True:
                if (serial_handle(uart_command, uart_port)):
                    ack_num += 1
                break
        if ack_num == 4:
            print 'respond'
        else:
            print 'not all acks all'

    def handle_arr_msg(self, uart_command):
        """
        Handle messages that come in as arrays
        @param uart_command: 
        @return: 
        """
        ack_num = 0

        count = 0
        for uart_port, single_uart_command in uart_command.iteritems():
            count += 1
            if len(single_uart_command) > 0:
                single_command = json.dumps(single_uart_command).strip('"')
                if serial_handle(single_command, uart_port):
                    ack_num += 1
        if ack_num == count:
            print 'response'
        else:
            print 'not all acks'

    def handle_other_msg(self, uart_command, uart_port):
        """
        Handle all other messages such as single leds,
        firmware or status messages
        @param uart_command: 
        @param uart_port: 
        @return: 
        """

        if(serial_handle(uart_command, uart_port)):
            print 'ack okay'
        else:
            print 'ack not okay'

    def allocate(self, incoming_data):
        """
        Allocate incoming data to whatever micro command 
        it is supposed to be 
        @param incoming_data: 
        @return: None
        """
        try:
            json_data = json.loads(incoming_data.replace(",}", "}"), encoding='utf8')
        except Exception as e:
            print 'NOT A VALID JSON'
            return
        response = ""
        if all(key in json_data for key in
               ("action", "category", "component", "component_id", "value")):
            msg = MessageHandler(json_data)
            response, (uart_command, uart_port) = msg.process_command()

            if DEBUG:
                print 'response:', response
                print 'uart com :', uart_command
                print 'uart port: ', uart_port

            if uart_port == "ALL":
                self.handle_all_msg(uart_command)

            elif uart_port == "ARRAY":
                self.handle_arr_msg(uart_command)

            else:
                self.handle_other_msg(uart_command, uart_port)

        print 'returning'


def tcp_handler(sock):
    """
    Main tcp handler which cycles through 
    readable file descriptors to check for 
    any incoming tcp packets. Allows only 5 
    readable connections, then drops the ones
    that aren't used. There is a single socket
    as the main file descriptor, followed by 
    other connections, which get culled when
    more than 5.
    @param sock: 
    @return: None
    """
    inputs = [sock]
    outputs = []
    message_queues = {}
    data_handler = DataHandler()
    try:
        while inputs:

            if len(inputs) > 5:
                for t in range(1,len(inputs)-1):
                    inputs[t].close()
                inputs = [inputs[0], inputs[len(inputs)-1]]

            readable, writable, exceptional = select.select(inputs, [], [sock], 1)
            for s in readable:
                if s is sock:
                    connection, client_address = s.accept()
                    if DEBUG:
                        print 'Connect', client_address
                    connection.setblocking(0)
                    inputs.append(connection)

                    message_queues[connection] = Queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        if DEBUG:
                            print 'Data:', data
                        # add to queue if response
                        message_queues[s].put(data)
                        data_handler.allocate(data)
                        if s not in outputs:
                            outputs.append(s)
                    else:
                        if DEBUG:
                            print 'Closing:', s
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        # remove from queue
                        del message_queues[s]

    except Exception as e:
        return


def serial_worker():
    """
    Serial thread which listens for incoming
    unsolicted messages
    @return: 
    """
    # TODO: include readable, writable, exceptional in here
    ser = serial.Serial('/dev/ttyO1', 115200)
    print 'setting up serial'

    while True:
        # TODO: check lock for uart here before proceeding
        incoming_command = ""
        start_char = ser.read(1)
        incoming_command += start_char

        if ord(start_char) == 0xe8:
            length = ser.read(1)
            incoming_command += length
            for i in range(ord(length)):
                cmd_byte = ser.read(1)
                incoming_command += cmd_byte
            checksum = ser.read(1)
            incoming_command += checksum
            stop_char = ser.read(1)
            incoming_command += stop_char
            print ":".join("{:02x}".format(ord(c)) for c in incoming_command)
            ser.write(incoming_command)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST, PORT = args.h, args.p

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    serial_thread = threading.Thread(target=serial_worker)
    serial_thread.daemon = True
    serial_thread.start()

    server_address = (HOST, int(PORT))
    print 'Starting server on:', server_address

    sock.bind(server_address)
    sock.setblocking(0)
    sock.listen(1)
    tcp_handler(sock)

