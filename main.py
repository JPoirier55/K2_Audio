import SocketServer
import sys, os
import uart
import argparse

class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        # print "{} wrote:".format(self.client_address[0])
        # print data
        # print self.finish
        # print self.server
        # print self.request
        command_handler = uart.CommandHandler(data)
        command_handler.process_command()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide port and host for UDP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST,PORT = args.h, args.p
    server = SocketServer.UDPServer((HOST, int(PORT)), UDPHandler)
    server.serve_forever()
