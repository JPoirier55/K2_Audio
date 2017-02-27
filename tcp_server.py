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
import Queue
import threading
import SocketServer
import serial
DEBUG = True
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
GLOBAL_QUEUE = Queue.Queue()


def worker():
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
        item = GLOBAL_QUEUE.get()
        ser = serial.Serial(item[1], 115200)
        ser.write(str(item[0]) + "\r\n")


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
        if "{" not in self.data:
            return
        print "_____", self.data, "  _________"
        print ':'.join(x.encode('hex') for x in self.data)

        json_data = json.loads(self.data)
        if all(key in json_data for key in ("action", "category", "component", "component_id", "value")):
            msg = MessageHandler(json_data)
            response, (uart_command, uart_port) = msg.process_command()
            if not uart_port or not uart_command:
                self.request.sendall(json.dumps(response) + '\n')
                return
            elif uart_port == "ALL":
                for uart_port in UART_PORTS:
                    GLOBAL_QUEUE.put((uart_command, uart_port))
            elif uart_port == "ARRAY":
                for uart_port, single_uart_command in uart_command.iteritems():
                    if len(single_uart_command) > 0:
                        GLOBAL_QUEUE.put((json.dumps(single_uart_command), uart_port))
            else:
                print 'Output: ', uart_port
                GLOBAL_QUEUE.put((uart_command, uart_port))
            self.request.sendall(json.dumps(response))
        else:
            self.request.sendall(error_response(1)[0] + '\n')


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    Built in for Threaded SocketServer
    """
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST, PORT = args.h, args.p
    server = ThreadedTCPServer((HOST, int(PORT)), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    queue_thread = threading.Thread(target=worker)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    queue_thread.daemon = True
    queue_thread.start()

    if DEBUG:
        print "Server loop running in thread:", server_thread.name
        print 'Global Queue running in thread: ', queue_thread.name

    server.serve_forever()
