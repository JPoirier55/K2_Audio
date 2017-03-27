import socket
import sys
import json
import multiprocessing
import select
import datetime
import errno
import serial
from message_utils import MessageHandler

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the address given on the command line
server_address = ('0.0.0.0', 65000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.setblocking(0)
sock.listen(1)
inputs = [sock]
while inputs:
    readable, writable, exceptional = select.select(inputs, [], [sock], 5)
    for r in readable:
        if r is sock:
            cnct, trt = sock.accept()
            inputs.append(cnct)
            while True:
                print 'connected', trt
                dat = cnct.recv(1024)

                if dat:
                    print dat
                else:
                    break
        # if not readable[0]:
        #     print 'closing'
        #     break
        # else:
        #     print 'waiting for data'
        #     incoming_data = cnct.recv(1024)
        #     if incoming_data == "":
        #         print 'done'
        #         cnct.close()
        #         break
        #     else:
        #         try:
        #             json_data = json.loads(incoming_data.replace(",}", "}"), encoding='utf8')
        #             print json_data
        #         except Exception as e:
        #             print 'NOT A VALID JSON'

            # response = ""
            # if all(key in json_data for key in ("action", "category", "component", "component_id", "value")):
            #     msg = MessageHandler(json_data)
            #     response, (uart_command, uart_port) = msg.process_command()
            #
            #     ser = serial.Serial('/dev/ttyO4', 115200)
            #     command = bytearray.fromhex(uart_command)
            #     ser.write(command)
            #     ser.close()


# def tcp_worker(data):
#     print data
#
# while True:
#         print 'waiting...'
#         connection, client_address = sock.accept()
#         print 'connected ', client_address
#         while True:
#             data = connection.recv(1024)
#             worker = multiprocessing.Process(target=tcp_worker, args=(data,))
#             print 'tcp thread starting, ', worker.name
#             print 'children  ', multiprocessing.active_children()
#             worker.start()
#             worker.join()


# while True:
#     print >>sys.stderr, 'waiting for a connection'
#     connection, client_address = sock.accept()
#     try:
#         print >>sys.stderr, 'client connected:', client_address
#         while True:
#
#             data = connection.recv(1024)
#
#             print data
#             print ":".join("{:02x}".format(ord(c)) for c in data)
#             json_data = json.loads(data.replace(",}", "}"))
#             print json_data
#             if data:
#                 continue
#             else:
#                 break
#     finally:
#         connection.close()