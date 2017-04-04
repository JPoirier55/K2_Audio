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
import socket
import json
import time
DEBUG = True

def client():
    while True:
        TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_CLIENT.connect(('0.0.0.0', 65000))
        led_message = {"category": "BTN", "component": "LED", "component_id": 'ALL', "action": "SET", "value": "1"}
        TCP_CLIENT.sendall(json.dumps(led_message))
        print 'sent'
        time.sleep(.5)
    # TCP_CLIENT.close()

    # for rate in range(2):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "CYC", "component_id": 'SLO', "action": "SET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()

    # TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TCP_CLIENT.connect(('0.0.0.0', 65000))
    # led_message = {"category": "CFG", "component": "RTE", "component_id": 'SLO', "action": "SET", "value": "1"}
    # TCP_CLIENT.sendall(json.dumps(led_message))
    # resp = TCP_CLIENT.recv(1024)
    # print 'Response:', resp
    # TCP_CLIENT.close()

    # for button_num in range(203):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "BTN", "component": "LED", "component_id": button_num, "action": "SET", "value": "1"}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "RTE", "component_id": 'SLO', "action": "SET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "RTE", "component_id": 'FST', "action": "SET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "CYC", "component_id": 'FST', "action": "SET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "CYC", "component_id": 'SLO', "action": "SET", "value": rate}
    #     print ' this is hwere thers an issues'
    #     print led_message
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "ENC", "component_id": 'SEN', "action": "SET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "RTE", "component_id": 'SLO', "action": "GET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "RTE", "component_id": 'FST', "action": "GET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "CYC", "component_id": 'FST', "action": "GET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "CYC", "component_id": 'SLO', "action": "GET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "CFG", "component": "ENC", "component_id": 'SEN', "action": "GET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "ENC", "component": "POS", "component_id": '0', "action": "SET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()
    #
    # for rate in range(10):
    #     TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     TCP_CLIENT.connect(('0.0.0.0', 65000))
    #     led_message = {"category": "ENC", "component": "DIS", "component_id": '0', "action": "SET", "value": rate}
    #     TCP_CLIENT.sendall(json.dumps(led_message))
    #     resp = TCP_CLIENT.recv(1024)
    #     print resp
    #     TCP_CLIENT.close()

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
    client()
    # parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
    # parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    # parser.add_argument('--p', '--PORT', default=65500, help='Port (default 65500)')
    #
    # args = parser.parse_args()
    # HOST, PORT = args.h, args.p
    # server = ThreadedTCPServer((HOST, int(PORT)), ThreadedTCPRequestHandler)
    # ip, port = server.server_address
    #
    # # Start a thread with the server -- that thread will then start one
    # # more thread for each request
    # server_thread = threading.Thread(target=server.serve_forever)
    #
    # # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    # server_thread.start()
    #
    #
    # if DEBUG:
    #     print "Server loop running in thread:", server_thread.name
    #
    # server.serve_forever()
