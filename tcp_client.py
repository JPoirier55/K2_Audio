import socket
import json
import binascii

HOST,PORT = '0.0.0.0', 65001

class MicroMessageHandler:

  def __init__(self, message):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((HOST,PORT))
    
    self.message = message
    self.category = self.message[0:6]
    self.cid = self.message[7:10]
    self.value = self.message[11:14]
  
  def handle_message(self):
    if self.category == 'BTN_SW':
      build_dict = {'category': 'BTN',
                    'component': 'SW',
                    'component_id': self.cid,
                    'action': '=',
                    'value': self.value}
    
    tcp_message = json.dumps(build_dict)
    self.send_tcp(tcp_message)
  
  def send_tcp(self, tcp_message):
    self.socket.sendall(tcp_message)
    self.socket.close()
    