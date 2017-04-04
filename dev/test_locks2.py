import serial
from locks import *
import time

while True:
    if lock1.acquire():
        print 'got it on test locks 2'
        time.sleep(10)
        print 'lock released from 2'
        lock1.release()
    else:
        print 'lock held'
