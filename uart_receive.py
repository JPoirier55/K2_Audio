import serial
import select
import json
from threading import Thread

class SerialReceiveHandler:
    def __init__(self, baudrate=115200, timeout=5):
        self.uarts = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
        self.setup_listeners()

    def setup_listeners(self):
        sers = []
        for uart in self.uarts:
          ser = serial.Serial(uart, baudrate=115200, timeout=5)
          sers.append(ser)
        while 1:
          readable, writable, exceptional = select.select(sers, [], sers)
          for s in readable:
            var = s.readline()
            print 'incoming: ', s.port, ' ', var
        ser.close()

if __name__ == '__main__':
    SerialReceiveHandler()
