import json

ex_packet = "BTN_SW 034 001"

def parse_packet(packet):
  cmd = packet[0:5]
  cid = packet[7:10]
  val = packet[11:14]
  
  print ','.join((cmd, cid, val))
  
if __name__=='__main__':
  parse_packet(ex_packet)
  
  