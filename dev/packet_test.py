import json
import time
# ex_packet = "BTN_SW 034 001"
#
# def parse_packet(packet):
#   cmd = packet[0:5]
#   cid = packet[7:10]
#   val = packet[11:14]
  
  # print ','.join((cmd, cid, val))

import socket
import sys
import random

HOST, PORT = "0.0.0.0", 65001
data = {"category": "CFG", "component": "CYC", "component_id": "FST", "action": "SET", "value": ""}
data2 = {"category": "BTN","component": "LED","component_id": ["34", "35", "67", "123", "203"],"action": "SET", "value":"1"}

# SOCK_DGRAM is the socket type to use for UDP sockets

# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
for i in range(25):
    r = random.randrange(0, 7)
    try:
        # Connect to server and send data
        data2['value'] = str(r)
        d = json.dumps(data2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))

        sock.send(d + "\n")
        # Receive data from the server and shut down
        received = sock.recv(1024)
        print "Received: {}".format(received)

    finally:
        sock.close()



