import socket

        
class UDPSender:
    def __init__(self, host, port):
      self.host = host
      self.port = port
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      
    def send_datagram(self, message):
      self.sock.sendto(message + "\n", (self.host, self.port))
