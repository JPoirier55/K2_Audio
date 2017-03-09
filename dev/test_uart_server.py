import serial

ser = serial.Serial('/dev/ttyO4', 115200)


while True:
    while True:
        print "{:02x}".format(ord(ser.read()))
