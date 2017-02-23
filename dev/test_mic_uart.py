import serial
import time
import json

dict = {'category':'LED', '':'ON'}
t = {'category':'BN_LED','id':'034', 'value':'003'}

cmd = "BN_LED 64 7"
cmd1 = "BN_LED 23 7"
cmd2 = "BN_LED 5 7"
cmd3 = "BN_LED 4 7"
cmd4 = "BN_LED 6 7"
# cmd2 = {"category":"BN_LED","id":["64","45","67","23"], "value":"7"}
# cmd3 = {"category":"BN_LED","id":"ALL", "value":"7"}
# cmd4 = {"category":"S_RATE","value":"7"}
# cmd5 = {"category":"F_RATE","value":"6"}
# cmd6 = {"category":"S_DCYC","value":"5"}
# cmd7 = {"category":"F_DCYC","value":"4"}
# cmd8 = {"category":"E_SENS","value":"3"}
# c =    {"category": "BN_LED", "id": "34", "value": "1"}
# arr = [cmd,cmd2,cmd3,cmd4,cmd5,cmd6,cmd7,cmd8]
arr2 = [cmd, cmd1, cmd2,cmd3,cmd4]
test = {'BN_LED': "test"}
#print ':'.join(x.encode('hex') for x in test)
ser = serial.Serial('/dev/ttyO1', 115200)

for c in arr2:
    print 'sending ', c
    ser.write(c+"\r\n")
    time.sleep(.1)

ser.close()
