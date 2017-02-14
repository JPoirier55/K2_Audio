import socket
import sys
import time
from subprocess import check_output

def get_lock(process_name):
    # Without holding a reference to our socket somewhere it gets garbage
    # collected when the function exits
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        get_lock._lock_socket.bind('\0' + process_name)
        print 'I got the lock'
    except socket.error:
        print 'lock exists'
        sys.exit()

def check_pid(process_name):
    
    return check_output(["pidof", process_name])


while True:
    t = check_pid('python uart_receive.py')
    print t
    time.sleep(3)