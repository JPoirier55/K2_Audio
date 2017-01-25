import SocketServer
import sys, os
sys.path.append(os.path.abspath("."))
import uart

class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "{} wrote:".format(self.client_address[0])
        print data
        uart.process_command(data)

if __name__ == '__main__':
    HOST,PORT = '0.0.0.0', 12345
    server = SocketServer.UDPServer((HOST, PORT), UDPHandler)
    server.serve_forever()
