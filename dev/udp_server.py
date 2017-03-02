import SocketServer
import sys, os
import argparse
#import uart_client

class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
      data = self.request[0].strip()
      print data
      socket = self.request[1]
      #uart_client.CommandHandler(data).process_command()

      
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide port and host for UDP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST,PORT = args.h, args.p
    print HOST, PORT
    server = SocketServer.UDPServer((HOST, int(PORT)), UDPHandler)
    server.serve_forever()
