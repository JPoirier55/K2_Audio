import Adafruit_BBIO.GPIO as GPIO
import time
import serial
#GPIO.setup('P8_8', GPIO.OUT)
GPIO.setup('P8_7', GPIO.IN)
GPIO.setup('P8_8', GPIO.IN)
GPIO.setup('P8_9', GPIO.OUT)
GPIO.setup('P8_10', GPIO.OUT)


ser1 = serial.Serial('/dev/ttyO4', 115200)
ser2 = serial.Serial('/dev/ttyO1', 115200)

def read_input(ser):
    cmd = ""
    while True:
        # TODO: check lock for that uart port in tcp_server
        var = ser.read(1)
        print var
        if ord(var) == 0xee:
            cmd += var
            break
        else:
            cmd += var
    return cmd

def start():
    while True:
        if GPIO.input("P8_7"):
            ser1.flushInput()
            GPIO.output("P8_9", GPIO.HIGH)
            print 'gpio 7'
            cmd = read_input(ser1)
            print ":".join("{:02x}".format(ord(c)) for c in cmd)
            ser1.write(bytearray.fromhex('E8020200ECEE'))
            GPIO.output("P8_9", GPIO.LOW)

        if not GPIO.input("P8_8"):
            ser2.flushInput()
            GPIO.output("P8_10", GPIO.HIGH)
            print 'gpio 8'
            cmd = read_input(ser2)
            print ":".join("{:02x}".format(ord(c)) for c in cmd)


if __name__ == '__main__':
    start()