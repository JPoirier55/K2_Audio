import serial
import Adafruit_BBIO.GPIO as GPIO
import select
import time
import sys

GPIO.setup('P8_39', GPIO.OUT)
GPIO.setup('P8_40', GPIO.IN)
GPIO.setup('P8_41', GPIO.OUT)
GPIO.setup('P8_42', GPIO.IN)
GPIO.setup('P8_43', GPIO.OUT)
GPIO.setup('P8_44', GPIO.IN)
GPIO.setup('P8_45', GPIO.OUT)
GPIO.setup('P8_46', GPIO.IN)

GPIO.output('P8_39', GPIO.LOW)
GPIO.output('P8_41', GPIO.LOW)
GPIO.output('P8_43', GPIO.LOW)
GPIO.output('P8_45', GPIO.LOW)


RTS = ['P8_45', 'P8_43', 'P8_41', 'P8_39']
CTS = ['P8_46', 'P8_44', 'P8_42', 'P8_40']
UARTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']

exceptions = ['E8039020039EEE', 'E80290108AEE', 'E8039011028EEE',
              'E8039021039FEE', 'E8039022029FEE', 'E8039023019FEE',
              'E80390300FBAEE']


def send_msg(rts, cts, msg, uart):
    low = True
    while True:
        print 'loop'
        if low:
            low = False
            GPIO.output(rts, GPIO.HIGH)
        else:
            low = True
            GPIO.output(rts, GPIO.LOW)

        if GPIO.input(cts):
            print 'sending', uart
            ser = serial.Serial(uart, 115200)
            ser.write(msg)
            print 'wrote', ":".join("{:02x}".format(c) for c in msg)
            incoming_command = ""
            while True:
                var = ser.read(1)
                print ord(var)
                if ord(var) == 0xee:
                    incoming_command += var
                    print ":".join("{:02x}".format(ord(c)) for c in incoming_command)
                    break
                else:
                    incoming_command += var
            GPIO.output(rts, GPIO.LOW)
            break


def calculate_checksum_bytes(micro_cmd):
    sum = 0
    for i in range(len(micro_cmd) - 2):
        sum += micro_cmd[i]
    return sum % 0x100

if __name__ == "__main__":
    # print 'E80211{0:0{1}X}32EE'.format(32,2)
    while True:
        for i in range(len(exceptions)):
            send_msg(RTS[0], CTS[0], bytearray.fromhex(exceptions[i]), UARTS[0])
        for i in range(100):
            cm = bytearray([0xE8, 0x02, 0x11, i, 0, 0xEE])
            cm[-2] = calculate_checksum_bytes(cm)
            print ":".join("{:02x}".format(c) for c in cm)
            send_msg(RTS[0], CTS[0], cm, UARTS[0])
        for i in range(23):
            for j in range(2):
                cm = bytearray([0xE8, 0x03, 0x10, i, j, 0, 0xEE])
                cm[-2] = calculate_checksum_bytes(cm)
                print ":".join("{:02x}".format(c) for c in cm)
                send_msg(RTS[0], CTS[0], cm, UARTS[0])
        for i in range(60):
            for j in range(2):
                cm = bytearray([0xE8, 0x03, 0x10, i, j, 0, 0xEE])
                cm[-2] = calculate_checksum_bytes(cm)
                print ":".join("{:02x}".format(c) for c in cm)
                send_msg(RTS[1], CTS[1], cm, UARTS[1])
        for i in range(60):
            for j in range(2):
                cm = bytearray([0xE8, 0x03, 0x10, i, j, 0, 0xEE])
                cm[-2] = calculate_checksum_bytes(cm)
                print ":".join("{:02x}".format(c) for c in cm)
                send_msg(RTS[2], CTS[2], cm, UARTS[2])
        for i in range(5):
            for j in range(2):
                cm = bytearray([0xE8, 0x03, 0x10, i, j, 0, 0xEE])
                cm[-2] = calculate_checksum_bytes(cm)
                print ":".join("{:02x}".format(c) for c in cm)
                send_msg(RTS[3], CTS[3], cm, UARTS[3])
