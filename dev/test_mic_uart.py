import serial
import time
import json

dict = {'category':'LED', '':'ON'}
t = {'category':'BN_LED','id':'034', 'value':'003'}

cmd = {"category":"BN_LED","id":"64", "value":"7"}
cmd2 = {"category":"BN_LED","id":["64","45","67","23"], "value":"7"}
cmd3 = {"category":"BN_LED","id":"ALL", "value":"7"}
cmd4 = {"category":"S_RATE","value":"7"}
cmd5 = {"category":"F_RATE","value":"6"}
cmd6 = {"category":"S_DCYC","value":"5"}
cmd7 = {"category":"F_DCYC","value":"4"}
cmd8 = {"category":"E_SENS","value":"3"}
c =    {"category": "BN_LED", "id": "34", "value": "1"}
arr = [cmd,cmd2,cmd3,cmd4,cmd5,cmd6,cmd7,cmd8]
test = {'BN_LED': "test"}
#print ':'.join(x.encode('hex') for x in test)
ser = serial.Serial('/dev/ttyO4', 115200)

for c in arr:
  print 'sending ', c
  ser.write(json.dumps(c)+"\r\n")
  time.sleep(.05)

ser.close()
