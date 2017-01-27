import SocketServer
import sys, os
import argparse
import socket
import uart

class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
      data = self.request[0].strip()
      socket = self.request[1]
      command_handler = uart.CommandHandler(data)
      command_handler.process_command()
        
class UDPSender:
    def __init__(self, host, port):
      self.host = host
      self.port = port
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      
    def send_datagram(self, message):
      self.sock.sendto(message + "\n", (self.host, self.port))
      
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide port and host for UDP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST,PORT = args.h, args.p
    server = SocketServer.UDPServer((HOST, int(PORT)), UDPHandler)
    server.serve_forever()
