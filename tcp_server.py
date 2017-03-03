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
from message_utils import MessageHandler, error_response
import argparse
import threading
import SocketServer
import serial
import select
import Queue
import socket
import binascii

DEBUG = True
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
SERVER_QUEUE = Queue.Queue()
CLIENT_QUEUE = Queue.Queue()
MIDDLE_QUEUE = Queue.Queue()

TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCP_CLIENT.connect(("192.168.255.88", 65000))

def server_worker():
    """
    Threads for each TCP connection that is made.
    These workers retrieve from the global queue
    in a non-blocking form which is a characteristic
    of the python FIFO Queue.

    The messages that get pulled from the queue
    are tuples with form (uart_command, uart_port)
    @return: None
    """
    while True:
        item = SERVER_QUEUE.get()
        print item['request']
        MIDDLE_QUEUE.put(item)
        # ser = serial.Serial(item[1], 115200)
        # ser.write(str(item[0]) + "\r\n")
        ser = serial.Serial('/dev/ttyO1', 115200)
        ser.write('testing' + "\r\n")


def client_worker():
    while True:
        item = CLIENT_QUEUE.get()
        ref = MIDDLE_QUEUE.get()
        if(item == ref['uart_defs']):
            ref['request'].sendall(item)
        else:
            TCP_CLIENT.sendall("Thtat did not work!")


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

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
            if not uart_port or not uart_command:
                self.request.sendall(json.dumps(response) + '\n')
                return
            elif uart_port == "ALL":
                for uart_port in UART_PORTS:
                    SERVER_QUEUE.put((uart_command, uart_port))
            elif uart_port == "ARRAY":
                for uart_port, single_uart_command in uart_command.iteritems():
                    if len(single_uart_command) > 0:
                        s = json.dumps(single_uart_command).strip('"')
                        SERVER_QUEUE.put((s, uart_port))
            else:
                print 'Output: ', uart_port
                print CLIENT_QUEUE
                SERVER_QUEUE.put({'request': self.request, 'uart_defs': 'testing\r\n'})
            #self.request.sendall(json.dumps(response))
        else:
            print 'no'
            #self.request.sendall(error_response(1)[0] + '\n')


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
                #if serial_connection.inWaiting() > 0:
                    try:

                        incoming_message = serial_connection.readline()
                        print "Incoming uart message: [{0}] ".format(serial_connection.port), incoming_message
                        print CLIENT_QUEUE
                        CLIENT_QUEUE.put(incoming_message)


                        #msg_handler = MicroMessageHandler(incoming_message)
                        #msg_handler.handle_message()

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

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    server_queue_thread = threading.Thread(target=server_worker)
    client_queue_thread = threading.Thread(target=client_worker)
    serial_thread = threading.Thread(target=SerialReceiveHandler)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    server_queue_thread.daemon = True
    server_queue_thread.start()
    client_queue_thread.daemon = True
    client_queue_thread.start()
    serial_thread.daemon = True
    serial_thread.start()


    if DEBUG:
        print "Server loop running in thread:", server_thread.name
        print 'Global server Queue running in thread: ', server_queue_thread.name
        print 'Global client Queue running in thread: ', client_queue_thread.name
        print 'Global serial handler running in thread: ', serial_thread.name


    server.serve_forever()
