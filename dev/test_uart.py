import serial
import time

ser = serial.Serial('/dev/ttyO4', 115200)

while True:
	ser.write("Testing\r\n")
#	print 'Writing'
	time.sleep(1)


