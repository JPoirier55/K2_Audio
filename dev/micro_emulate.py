import serial

uarts = ['/dev/ttyO4', '/dev/ttyO2']
ser = serial.Serial(uarts[0], 115200)

def send_unsolicited():
    for i in range(1,0xCC):
        cmd = 'E80310{0:02X}0021EE'.format(i)
        print cmd
    # msgs = [bytearray.fromhex('E80310180021EE'),bytearray.fromhex('E80310150121EE')]
        msg = bytearray.fromhex(cmd)
        ser.write(msg)

    for i in range(0,101):
        cmd = 'E80211{0:02X}21EE'.format(i)
        print cmd
        # msgs = [bytearray.fromhex('E80310180021EE'),bytearray.fromhex('E80310150121EE')]
        msg = bytearray.fromhex(cmd)
        ser.write(msg)

    for i in range(4):
        cmd = 'E80390{0:02X}21EE'.format(i)
        print cmd
        # msgs = [bytearray.fromhex('E80310180021EE'),bytearray.fromhex('E80310150121EE')]
        msg = bytearray.fromhex(cmd)
        ser.write(msg)

    for i in range(4):
        cmd = 'E802800021EE'
        print cmd
        # msgs = [bytearray.fromhex('E80310180021EE'),bytearray.fromhex('E80310150121EE')]
        msg = bytearray.fromhex(cmd)
        ser.write(msg)

    for i in range(3):
        cmd = 'E803F0{0:02X}21EE'.format(i)
        print cmd
        # msgs = [bytearray.fromhex('E80310180021EE'),bytearray.fromhex('E80310150121EE')]
        msg = bytearray.fromhex(cmd)
        ser.write(msg)
    ser.close()

if __name__ == '__main__':
    send_unsolicited()

