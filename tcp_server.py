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

import SocketServer
import socket
import json
from message_utils import MessageHandler, error_response
import argparse
import Queue
from threading import Thread
import threading
DEBUG = True
import socket
import threading
import SocketServer
import serial
import time

ser = serial.Serial('/dev/ttyO5', 115200)

q = Queue.Queue()


def worker():
    while True:
        item = q.get()
        time.sleep(1)
        ser.write(item + "\n")


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024)
        cur_thread = threading.current_thread()

        json_data = json.loads(self.data)
        if all(key in json_data for key in ("action", "category", "component", "component_id", "value")):
            msg = MessageHandler(json_data)
            response, uart_command = msg.process_command()
            q.put(uart_command)
            self.request.sendall(json.dumps(response))
        else:
            self.request.sendall(json.dumps(error_response(1)) + '\n')


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 65000

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
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
    print "Server loop running in thread:", server_thread.name
    print 'queue_thread running in thread: ', queue_thread.name

    # client(ip, port, "Hello World 1")
    # client(ip, port, "Hello World 2")
    # client(ip, port, "Hello World 3")

    server.serve_forever()


#

#
# QUEUE_HANDLER = QueueHandler()
#
# def queue_runner(queue_handler):
#     while True:
#         msg = queue_handler.dequeue()
#         if msg is not None:
#             print 'ok'
#         else:
#             print 'not okay'



# class MyTCPHandler(SocketServer.BaseRequestHandler):
#
#     def setup(self):
#         print 'Setting up socket server and Queue...'
#         worker = Thread(target=queue_runner, args=QUEUE_HANDLER)
#         worker.setDaemon(True)
#         worker.start()
#
#     def handle(self):
#         """
#         Main handler method for TCP server
#         @return: None
#         """
#         self.data = self.request.recv(1024).strip()
#
#         if DEBUG:
#             print "{} wrote:".format(self.client_address[0])
#         print self.data
#
#         try:
#             json_data = json.loads(self.data)
#             if all(key in json_data for key in ("action", "category", "component", "component_id", "value")):
#                 msg = MessageHandler(json_data)
#                 print 'Adding msg to queue:', json_data
#                 QUEUE_HANDLER.enqueue(msg, self.request)
#                 #response = msg.process_command()
#                 #self.request.sendall(json.dumps(response))
#             else:
#                 self.request.sendall(json.dumps(error_response(1)) + '\n')
#
#         except Exception as e:
#             if DEBUG:
#                 print e
#             self.request.sendall(json.dumps(error_response(3)) + '\n')
#
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
#     parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
#     parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')
#
#     args = parser.parse_args()
#     HOST, PORT = args.h, args.p
#     server = SocketServer.TCPServer((HOST, int(PORT)), MyTCPHandler)
#     server.serve_forever()
