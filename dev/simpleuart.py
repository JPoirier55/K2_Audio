import serial
import Adafruit_BBIO.GPIO as GPIO
import select
import time

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


# #
# GPIO.add_event_detect("P8_40", GPIO.BOTH)
# GPIO.add_event_detect("P8_42", GPIO.BOTH)
# GPIO.add_event_detect("P8_44", GPIO.BOTH)
# GPIO.add_event_detect("P8_46", GPIO.BOTH)

# RTS_GPIOS = ['/sys/class/gpio/gpio70/value', '/sys/class/gpio/gpio72/value',
#              '/sys/class/gpio/gpio74/value', '/sys/class/gpio/gpio76/value']
# RTS_GPIO_EDGE_FDS = ['/sys/class/gpio/gpio70/edge', '/sys/class/gpio/gpio72/edge',
#                      '/sys/class/gpio/gpio74/edge', '/sys/class/gpio/gpio76/edge']
#
#
# CTS_GPIOS = ['/sys/class/gpio/gpio71/value', '/sys/class/gpio/gpio73/value',
#              '/sys/class/gpio/gpio75/value', '/sys/class/gpio/gpio77/value']
# CTS_GPIO_EDGE_FDS = ['/sys/class/gpio/gpio71/edge', '/sys/class/gpio/gpio73/edge',
#                      '/sys/class/gpio/gpio75/edge', '/sys/class/gpio/gpio77/edge']
#
ser = serial.Serial('/dev/ttyO1', 115200)

ser.write(bytearray.fromhex('E80242010255EE'))
while True:
    print ser.read(1)

# def serial_worker():
#     """
#     Serial thread which listens for incoming
#     unsolicted messages
#     @return:
#     """
#     gpio_fds = []
#     vals = []
#     while True:
#
#         for gpio in CTS_GPIOS:
#             open_file = open(gpio)
#             gpio_fds.append(open_file)
#
#         for gpio_edge_fd in CTS_GPIO_EDGE_FDS:
#             fd = open(gpio_edge_fd, 'w')
#             fd.write("both")
#
#         for fd in gpio_fds:
#             vals.append(fd.read())
#
#         readable, writable, exceptional = select.select([], [], gpio_fds, 5)
#         for e in exceptional:
#             if e == gpio_fds[0]:
#                 if int(vals[0]) == 1:
#                     print 'gpio 0'
#
#             elif e == gpio_fds[1]:
#                 if int(vals[1]) == 1:
#                     print 'gpio 1'
#
#             elif e == gpio_fds[2]:
#                 if int(vals[2]) == 1:
#                     print 'gpio 2'
#
#             elif e == gpio_fds[3]:
#                 if int(vals[3]) == 1:
#                     print 'gpio 3'
#
#         vals = []
#         gpio_fds = []

d = ['P8_45', 'P8_43', 'P8_41', 'P8_39']


def send_msg():
    low = True
    while True:

        if low:
            low = False
            GPIO.output('P8_45', GPIO.HIGH)
        else:
            low = True
            GPIO.output('P8_45', GPIO.LOW)

        if GPIO.input("P8_46"):
            print 'sending'
            ser = serial.Serial('/dev/ttyO1', 115200)
            ser.write(bytearray.fromhex('E8021005FFEE'))
            # ser.read(32)
            GPIO.output('P8_45', GPIO.LOW)

            time.sleep(1)
            print 'here?'

        time.sleep(1)


'''
        # for gpio in d:
        #     GPIO.output(gpio, GPIO.HIGH)
        # 
        #     while True:
        #         if GPIO.event_detected("P8_40"):
        #             print 'sending'
        #             ser = serial.Serial('/dev/ttyO1', 115200)
        #             ser.write('E80310050021EE')
        #             break
        #         if GPIO.event_detected("P8_42"):
        #             print 'sending'
        #             ser = serial.Serial('/dev/ttyO2', 115200)
        #             ser.write('E80310050021EE')
        #             break
        #         if GPIO.event_detected("P8_44"):
        #             print 'sending'
        #             ser = serial.Serial('/dev/ttyO4', 115200)
        #             ser.write('E80310050021EE')
        #             break
        #         if GPIO.event_detected("P8_46"):
        #             print 'sending'
        #             ser = serial.Serial('/dev/ttyO5', 115200)
        #             ser.write('E80310050021EE')
        #             break
        #         print 'trying'
        #         time.sleep(.5)
        #     time.sleep(.5)
        #     GPIO.output(gpio, GPIO.LOW)
'''
if __name__ == "__main__":

    send_msg()
    # low = True
    # GPIO.output("P8_39", GPIO.HIGH)
    # GPIO.output("P8_41", GPIO.HIGH)
    # GPIO.output("P8_43", GPIO.HIGH)
    # GPIO.output("P8_45", GPIO.HIGH)
    # while True:
    #     time.sleep(1)
    #     if low:
    #         print 'HIGH'
    #         low = False
    #         GPIO.output("P8_45", GPIO.HIGH)
    #     else:
    #         print 'LOW'
    #         low = True
    #         GPIO.output("P8_45", GPIO.LOW)

    # send_msg()
    # serial_worker()
    # print GPIO.setup('P8_41', GPIO.IN)
    # GPIO.setup('P8_42', GPIO.IN)
    # GPIO.setup('P8_43', GPIO.IN)
    # GPIO.setup('P8_44', GPIO.IN)

    # GPIO.add_event_detect("P8_40", GPIO.BOTH)
    # # print GPIO.event_detected("P8_41")
    # while True:
    #     if GPIO.event_detected("P8_40"):
    #         print "event detected!"

    # ser = serial.Serial('/dev/ttyO4', 115200)
    # # ba = bytearray.fromhex('E80E42078564523785634455667788942BEE')
    # # ba = bytearray.fromhex('E80280006AEE')
    # # ba = bytearray.fromhex('E803100E020BEE')
    # ba = bytearray.fromhex('E802112520EE')
    # # print 'sum: ', calculate_checksum(ba)
    # ser.write(ba)
    # #
    # while True:
    #     t  = ser.read(1)
    #     print hex(ord(t))
