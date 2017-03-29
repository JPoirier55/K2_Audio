import serial

ser = serial.Serial('/dev/ttyO4', 115200)

ser.write(bytearray.fromhex('E80E4207856452378563445566778894EEEE'))

while True:
    t  = ser.read(1)
    print hex(ord(t))
