"""
FILE:   tcp_client.py
DESCRIPTION: TCP client module to handle messages from micro->beaglebone->DSP
WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
2/10/17          JDP                original
"""

import socket
import json
import binascii

HOST, PORT = '0.0.0.0', 65001


class MicroMessageHandler:

    def __init__(self, message):
        """
        Initialize socket connection to DSP
        host and port. Parse message into
        category, cid and value when class is
        instantiated
        @param message: Incoming message from the
        micro
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        self.message = message
        self.category = self.message[0:6]
        self.cid = self.message[7:10]
        self.value = self.message[11:14]

    def handle_message(self):
        """
        Converter method which takes in micro
        command and converts it back into JSON
        for sending to DSP
        @return: None
        """
        if self.category == 'BTN_SW':
            print 'btn switch'

    def send_tcp(self, tcp_message):
        """
        Send tcp back to DSP after building
        message from micro
        @param tcp_message: JSON message to DSP
        @return: None
        """
        self.socket.sendall(tcp_message)
        self.socket.close()


def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

if __name__ == "__main__":
    while 1:
        client('0.0.0.0', 65001, "data")
