import socket
import sys
import Queue
import select

SERVER_RUNNING = False

def start_connection():

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address given on the command line
    server_address = ('0.0.0.0', 65000)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    sock.setblocking(0)
    sock.listen(1)
    return sock


def run_server(sock):
    inputs = [sock]
    outputs = []
    message_queues = {}
    try:
        while inputs:
            if len(inputs) > 5:
                for t in range(1,len(inputs)-1):
                    inputs[t].close()
                inputs = [inputs[0], inputs[len(inputs)-1]]

            readable, writable, exceptional = select.select(inputs, [], [sock], 1)
            for s in readable:
                print 'BEFORE LOOP'
                for t in inputs:
                    print t

                if s is sock:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    print >> sys.stderr, 'new connection from', client_address
                    connection.setblocking(0)
                    inputs.append(connection)
                    print 'IN LOOP'
                    for t in inputs:
                        print t

                    # Give the connection a queue for data we want to send
                    message_queues[connection] = Queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        # A readable client socket has data
                        print >> sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
                        message_queues[s].put(data)
                        # Add output channel for response
                        if s not in outputs:
                            outputs.append(s)
                    else:
                        # Interpret empty result as closed connection
                        print >> sys.stderr, 'closing', client_address, 'after reading no data'
                        # Stop listening for input on the connection
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()

                        # Remove message queue
                        del message_queues[s]
    except Exception as e:
        SERVER_RUNNING = False
        return


if __name__ == '__main__':
    while True:
        if not SERVER_RUNNING:
            new_sock = start_connection()
            run_server(new_sock)
            SERVER_RUNNING = True


