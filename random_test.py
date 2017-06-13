
import random
import serial
from copy import deepcopy
import time
import logging

logging.basicConfig(filename='/home/debian/K2_Audio/test_log.log', level=logging.DEBUG)

def calculate_checksum(micro_cmd):
    sum = 0
    for i in range(len(micro_cmd) - 2):
        sum += micro_cmd[i]
    return sum % 0x100

# SINGLE_TEST_LED = bytearray.fromhex('E80340000000EE')
# MICRO_ACK = bytearray.fromhex('E8018069EE')
#
# micro_0_leds = [150, 151, 152, 153, 154]
# commands = []
#
# for led in micro_0_leds:
#     SINGLE_TEST_LED[3] = led
#     SINGLE_TEST_LED[4] = random.randrange(0, 8)
#     SINGLE_TEST_LED[5] = calculate_checksum(SINGLE_TEST_LED)
#     tmp = deepcopy(SINGLE_TEST_LED)
#     commands.append(tmp)
#     # print ":".join("{:02x}".format(c) for c in SINGLE_TEST_LED)
# for cmd in commands:
#     logging.debug(":".join("{:02x}".format(c) for c in cmd))

ALL_LEDS = bytearray.fromhex('E8034001F800EE')
ALL_LEDS_OFF = bytearray.fromhex('E8034000F800EE')
SINGLE_TEST_ = bytearray.fromhex('E80340020100EE')

ser = serial.Serial('/dev/ttyO1', 115200, timeout=1)

t = deepcopy(SINGLE_TEST_)
a = deepcopy(ALL_LEDS_OFF)
a[-2] = calculate_checksum(ALL_LEDS_OFF)

b = deepcopy(ALL_LEDS)
b[-2] = calculate_checksum(ALL_LEDS)

t[-2] = calculate_checksum(SINGLE_TEST_)

print ":".join("{:02x}".format(c) for c in a)
print ":".join("{:02x}".format(c) for c in b)

ser.write(t)
time.sleep(2)
ser.write(b)
time.sleep(2)
ser.write(a)




# while True:
#     for cmd in commands:
#         logging.debug("Writing: ")
#         logging.debug(":".join("{:02x}".format(c) for c in cmd))
#         ser.write(cmd)
#         incoming_command = ""
#         while True:
#             logging.debug('Reading from serial:')
#             var = ser.read(1)
#             if len(var) != 0:
#                 if ord(var) == 0xee:
#                     incoming_command += var
#                     if incoming_command == MICRO_ACK:
#                         logging.debug(":".join("{:02x}".format(ord(c)) for c in incoming_command))
#                         break
#                 else:
#                     incoming_command += var
#             else:
#                 break
#     logging.debug("Waiting 10 seconds")
#     time.sleep(10)

