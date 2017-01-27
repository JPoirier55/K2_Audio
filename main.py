import SocketServer
import sys, os
import argparse
import ethernet

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide port and host for UDP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST,PORT = args.h, args.p
    server = SocketServer.UDPServer((HOST, int(PORT)), ethernet.UDPHandler)
    server.serve_forever()
