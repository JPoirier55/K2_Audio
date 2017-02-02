import serial

ser = serial.Serial('/dev/ttyO1', 115200)

while 1:
  var = ser.readline()
  print var
  #print ':'.join(x.encode('hex') for x in var)
  
  
ser.close()