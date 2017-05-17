
import select

"""
FILE:   globals.py
DESCRIPTION: All global variables contained in one module used by 
tcp_server.py

WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
4/5/17          JDP                original
"""

import Adafruit_BBIO.GPIO as GPIO

GPIO.setup('P8_39', GPIO.IN)
GPIO.setup('P8_41', GPIO.IN)
GPIO.setup('P8_43', GPIO.IN)
GPIO.setup('P8_45', GPIO.IN)

GPIO.setup('P8_40', GPIO.OUT)
GPIO.setup('P8_42', GPIO.OUT)
GPIO.setup('P8_44', GPIO.OUT)
GPIO.setup('P8_46', GPIO.OUT)

GPIO.output("P8_40", GPIO.LOW)
GPIO.output("P8_42", GPIO.LOW)
GPIO.output("P8_44", GPIO.LOW)
GPIO.output("P8_46", GPIO.LOW)

RTS_GPIOS = ['/sys/class/gpio/gpio70/value', '/sys/class/gpio/gpio72/value',
             '/sys/class/gpio/gpio74/value', '/sys/class/gpio/gpio76/value']
GPIO_EDGE_FDS = ['/sys/class/gpio/gpio70/edge', '/sys/class/gpio/gpio72/edge',
                 '/sys/class/gpio/gpio74/edge', '/sys/class/gpio/gpio76/edge']
import time
import binascii
import serial
import sys
# GPIO.wait_for_edge("P8_45", GPIO.RISING)
GPIO.add_event_detect("P8_45", GPIO.RISING)
CTS_GPIOS = ['P8_46', 'P8_44', 'P8_42', 'P8_40']

ser = serial.Serial('/dev/ttyO1', 115200)

# time.sleep(.5)
# t = open(RTS_GPIOS[0])
# f = t.read()


def read_serial_generic(ser):
    """
    Method to read any incoming message that
    falls within the format of our protocol between
    Beaglebone and micro. Creates a bytearray for command.
    Example message: E8021005FFEE
    See command_map.py for all message
    parameters and definitions

    @param ser: Serial object being read from
    @return: Tuple of message in bytes, and checksum
    """
    checksum = 0
    ba = bytearray()
    print 'read serial generic'
    try:
        start_char = ser.read(1)
        # print binascii.unhexlify(start_char)
    except Exception as e:
        print "failed", e
        sys.exit(0)

    ba.append(start_char)
    print ba
    print 'here'
    print ":".join("{:02x}".format(c) for c in ba)
    if ord(start_char) == 0xe8:
        length = ser.read(1)
        ba.append(length)
        print ":".join("{:02x}".format(c) for c in ba)
        # Add switch ids corresponding to length
        for i in range(ord(length)):
            cmd_byte = ser.read(1)
            ba.append(cmd_byte)
            print ":".join("{:02x}".format(c) for c in ba)
        checksum = ser.read(1)
        ba.append(checksum)
        print ":".join("{:02x}".format(c) for c in ba)
        stop_char = ser.read(1)
        ba.append(stop_char)
        print ":".join("{:02x}".format(c) for c in ba)
    else:
        return None, None
    if len(ba) == 0:
        return None, None
    return ba, checksum

while True:
    if GPIO.event_detected("P8_45"):
        print 'RTS high'
        # GPIO.output("P8_46", GPIO.HIGH)

        t, c = read_serial_generic(ser)

    else:
        print 'RTS low'
    time.sleep(.2)


    # print f[0]
    # GPIO.output("P8_46", GPIO.LOW)
    # print 'RTS reset to low'
    # GPIO.output("P8_46", GPIO.LOW)
    # if GPIO.input("P8_45"):
    #     print' highi'
    #     time.sleep(.2)

    #     if not GPIO.input("P8_45"):
    #         time.sleep(.2)
    #         print 'highthenlow'
    #         GPIO.output("P8_46", GPIO.LOW)
    #     time.sleep(.2)
    # else:
    #     print' low'
    # time.sleep(.5)
    # t = open(RTS_GPIOS[0])
    # print t.read()
    #
    # readable, writable, exceptional = select.select([], [], [t], 0)
    #
    # if exceptional:
    #     print exceptional
    # time.sleep(.5)

    # if t.read() == str(1):
    #     print("HIGH")
    # else:
    #     print("LOW")


# while True:
#     for gpio in RTS_GPIOS:
#         open_file = open(gpio)
#         gpio_fds.append(open_file)
#
#     for gpio_edge_fd in GPIO_EDGE_FDS:
#         fd = open(gpio_edge_fd, 'w')
#         fd.write("both")
#
#     for fd in gpio_fds:
#         vals.append(fd.read())
#
#     readable, writable, exceptional = select.select([], [], gpio_fds, 1)
#     # Read all file descriptors in exceptional for gpios for rts
#     for e in exceptional:
#         if e == gpio_fds[0]:
#             if int(vals[0]) == 1:
#                 print gpio_fds[0]
#
#         elif e == gpio_fds[1]:
#             if int(vals[1]) == 1:
#                 print gpio_fds[0]
#
#         elif e == gpio_fds[2]:
#             if int(vals[2]) == 1:
#                 print gpio_fds[0]
#
#         elif e == gpio_fds[3]:
#             if int(vals[3]) == 1:
#                 print gpio_fds[0]
#
#     vals = []
#     gpio_fds = []