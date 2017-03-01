"""
FILE:   dsp_server.py
DESCRIPTION: Testing TCP server to simulate DSP

WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
2/21/17          JDP                original
"""

import argparse
import threading
import SocketServer
DEBUG = True


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
        print self.data


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    Built in for Threaded SocketServer
    """
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65500, help='Port (default 65500)')

    args = parser.parse_args()
    HOST, PORT = args.h, args.p
    server = ThreadedTCPServer((HOST, int(PORT)), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()


    if DEBUG:
        print "Server loop running in thread:", server_thread.name

    server.serve_forever()
