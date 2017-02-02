import serial
import time
import json

dict = {'STATUS':'LED', 'ACTION':'ON'}
ser = serial.Serial('/dev/ttyO1', 115200)
ser.write(json.dumps(dict)+"\n")
#while 1:
#  ser.write("testinhh\n")
#  print 'sending..'
#  time.sleep(1)

ser.close()
