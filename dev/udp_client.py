import socket

        
class UDPSender:
    def __init__(self, host, port):
      self.host = host
      self.port = port
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      
    def send_datagram(self, message):
      self.sock.sendto(message + "\n", (self.host, self.port))

if __name__ == '__main__':
    u = UDPSender('50.242.132.145', 65000)
    u.send_datagram("hello")
