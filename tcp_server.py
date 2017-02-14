import SocketServer
import json
from message_utils import MessageHandler, error_response
import argparse


DEBUG = True

class MyTCPHandler(SocketServer.BaseRequestHandler):
  
    def handle(self):
      # self.request is the TCP socket connected to the client
      self.data = self.request.recv(1024).strip()
      
      if DEBUG:
        print "{} wrote:".format(self.client_address[0])
        print self.data
      
      try:
        json_data = json.loads(self.data)
        if all (key in json_data for key in ("action", "category", "component_id", "value")):
          msg = MessageHandler(json_data)
          response = msg.process_command()
          self.request.sendall(json.dumps(response))
        else:
          self.request.sendall(json.dumps(error_response(1))+'\n')
        
      except Exception as e:
        if DEBUG:
          print e
        self.request.sendall(json.dumps(error_response(3))+'\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST,PORT = args.h, args.p
    server = SocketServer.TCPServer((HOST, int(PORT)), MyTCPHandler)
    server.serve_forever()