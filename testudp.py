import socket
import random
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

while 1:
  r = random.randint(1,200)
  s = '{"seat_id":' + str(r) +', "state":0}\00'
  #print s
  sock.sendto(s, ('0.0.0.0', 65000))
  time.sleep(.2)
