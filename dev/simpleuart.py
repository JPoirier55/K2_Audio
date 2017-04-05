import serial
import Adafruit_BBIO.GPIO as GPIO
import select

# GPIO.setup('P8_7', GPIO.IN)
# GPIO.setup('P8_8', GPIO.OUT)
# GPIO.setup('P8_9', GPIO.OUT)
# GPIO.setup('P8_10', GPIO.OUT)

# ser = serial.Serial('/dev/ttyO4', 115200)

# def calculate_checksum(micro_cmd):
#     sum = 0
#     for i in range(len(micro_cmd) - 2):
#         print micro_cmd[i]
#         sum += micro_cmd[i]
#     return sum%0x100
# def s():
#     while True:
#         GPIO.output("P8_8", GPIO.HIGH)
#
#         # if GPIO.input("P8_7"):
#         #     print 'on'
#         # else:
#         #     print 'off'
#         # gpio = GPIO.input("P8_7")
#         gpio = open('/sys/class/gpio/gpio69/value')
#         val = gpio.read()
#         gpio_edge = open('/sys/class/gpio/gpio69/edge', 'w')
#         gpio_edge.write("both")
#
#         r, w, e = select.select([], [], [gpio], 5)
#         if e:
#             if int(val) == 1:
#                 print 'sending'


# ba = bytearray.fromhex('E80E42078564523785634455667788942BEE')
# # print 'sum: ', calculate_checksum(ba)
# ser.write(ba)
#
# while True:
#     t  = ser.read(1)
#     print hex(ord(t))
import time
if __name__ == "__main__":

    # print GPIO.setup('P8_41', GPIO.IN)
    # GPIO.setup('P8_42', GPIO.IN)
    # GPIO.setup('P8_43', GPIO.IN)
    # GPIO.setup('P8_44', GPIO.IN)

    # print GPIO.add_event_detect("P8_41", GPIO.BOTH)
    # print GPIO.event_detected("P8_41")
    # while True:
    #     if GPIO.event_detected("P8_41"):
    #         print "event detected!"
    ser = serial.Serial('/dev/ttyO4', 115200)
    # ba = bytearray.fromhex('E80E42078564523785634455667788942BEE')
    # ba = bytearray.fromhex('E80280006AEE')
    # ba = bytearray.fromhex('E803100E020BEE')
    ba = bytearray.fromhex('E802112520EE')
    # print 'sum: ', calculate_checksum(ba)
    ser.write(ba)
    #
    while True:
        t  = ser.read(1)
        print hex(ord(t))