import serial
import select
import json
from threading import Thread
import time

class SerialReceiveHandler:
    def __init__(self, baudrate=115200, timeout=None):
        self.uarts = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
        self.timeout = timeout
        serial_listeners = self.setup_listeners()
        #self.setup_threads(serial_listeners)
        self.listen_serial(serial_listeners)

    def setup_listeners(self):
        sers = []
        for uart in self.uarts:
          try:
            ser = serial.Serial(uart, baudrate=115200, timeout=self.timeout)
            sers.append(ser)
          except serial.SerialException as e:
            print 'Serial Exception Thrown:  ', e
            continue
          
        return sers

    def listen_serial(self, sers):
        while 1:
          readable, writable, exceptional = select.select(sers, [], sers)
          for s in readable:
            if s.inWaiting()>0:
              try:
                var = s.readline()
                print 'incoming: ', s.port, ' ', var
              except serial.SerialException as e:
                print 'Cannot read line, Serial Exception Thrown:  ', e
                continue
        
    def setup_threads(self, sers):
        for ser in sers:
          thread = Thread(target=self.threaded_serial, args=(ser,))
          thread.start()

    def threaded_serial(self, ser):
        while True:
          if ser.inWaiting()>0:
            var = ser.readline()
            #print 'incoming: ', ser.port, ' ', var
            self.handle(var)
          
    def handle(self, data):
        print ' handling data: ', data        

if __name__ == '__main__':
    SerialReceiveHandler()
    #ser = serial.Serial('/dev/ttyO2', baudrate=115200, timeout=5)
    #while 1:
     # ser.write("hello")
     # print 'writing...'
     # time.sleep(1)