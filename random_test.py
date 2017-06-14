
import random
import serial
from copy import deepcopy
import time
import logging
from globals import *
import button_led_map

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

# ALL_LEDS = bytearray.fromhex('E8034001F800EE')
# ALL_LEDS_OFF = bytearray.fromhex('E8034000F800EE')
# SINGLE_TEST_ = bytearray.fromhex('E80340020100EE')
#
# ser = serial.Serial('/dev/ttyO1', 115200, timeout=1)
#
# t = deepcopy(SINGLE_TEST_)
# a = deepcopy(ALL_LEDS_OFF)
# a[-2] = calculate_checksum(ALL_LEDS_OFF)
#
# b = deepcopy(ALL_LEDS)
# b[-2] = calculate_checksum(ALL_LEDS)
#
# t[-2] = calculate_checksum(SINGLE_TEST_)
#
# print ":".join("{:02x}".format(c) for c in a)
# print ":".join("{:02x}".format(c) for c in b)
#
# ser.write(t)
# time.sleep(2)
# ser.write(b)
# time.sleep(2)
# ser.write(a)

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
    start_char = ser.read(1)
    ba.append(start_char)

    if ord(start_char) == 0xe8:
        length = ser.read(1)
        ba.append(length)
        # Add switch ids corresponding to length
        for i in range(ord(length)):
            cmd_byte = ser.read(1)
            ba.append(cmd_byte)
        checksum = ser.read(1)
        ba.append(checksum)
        stop_char = ser.read(1)
        ba.append(stop_char)

    return ba, checksum


class StartUpTester:
    """
    Sequence that is initialized when server starts. Runs as follows:

    1. Check all uart ports for acks back
    2. Light up all LEDS to be checked for broken ones, wait 5 seconds
    3. Shut all LEDs off
    4. Start carousel of LEDs until DSP sends status command

    """

    def __init__(self):
        """
        Init all serial ports and setup serial connections
        """
        self.uart_ports = UART_PORTS
        self.baudrate = SERIAL_BAUDRATE
        self.timeout = SERIAL_TIMEOUT
        self.sers = []
        self.setup_sers()

    def setup_sers(self):
        """
        Create list of serial file descriptors
        needed for running the initial start sequence

        @return: None
        """
        for uart in self.uart_ports:
            self.sers.append(serial.Serial(port=uart, baudrate=self.baudrate, timeout=self.timeout))

    def read_serial(self, ser, cmd_type):
        """
        Method to read incoming message from
        micro after sending message

        @param ser: serial object
        @return: 1 - checksum correct and ack received
                 2 - either checksum or ack not correct/received
        """
        # ba, checksum = read_serial_generic(ser)
        try:
            ba, checksum = read_serial_generic(ser)
            if DEBUG:
                print "READ SERIAL GENERIC OUTPUT", ":".join("{:02x}".format(c) for c in ba)
        except Exception:
            return 0

        c = calculate_checksum(ba)
        if cmd_type == 'sts':
            if c == ord(checksum) and ba[2] == 0x31:
                return 1
        elif cmd_type == 'led':
            print 'BA 2', ba[2]
            if c == ord(checksum) and ba == MICRO_ACK:
                return 1

        return 0

    def send_command(self, micro_cmd):
        """
        Send micro command for initial startup
        sequence, and read incoming ack

        @param micro_cmd: outgoing micro command
        @return: True - If all four acks have been received
                 False - If less than four received
        """
        micro_ack = 0
        for ser in self.sers:

            if DEBUG:
                print 'Current serial connection:', ser
            ser.write(micro_cmd)

            if micro_cmd[2] == 0x31:
                micro_ack += self.read_serial(ser, 'sts')
            else:
                micro_ack += self.read_serial(ser, 'led')

            # time.sleep(.1)
        if micro_ack == 4:
            return True
        return False

    def run_startup(self):
        """
        Run startup sequence of commands to
        check all four micros, then have all
        LEDs come on, wait 5 seconds, then
        turn off.

        @return: True - If everything worked
                 False - If an error occurred
        """
        if self.send_command(MICRO_STATUS):
            while True:
                self.send_command(ALL_LEDS)
                # time.sleep(.1)
                self.send_command(ALL_LEDS_OFF)
                # time.sleep(.1)
                self.run_blinky_sequence()
                # time.sleep(.1)
                self.send_command(ALL_LEDS_OFF)
        return False

    def run_blinky_sequence(self):
        """
        Iterate through LEDs on control board
        to turn on in the order 1-2-3-...202-203
        Each one has a wait of .1 seconds between
        turning on

        @return: None
        """
        # for i in range(8):
        for led in button_led_map.map_arrays['panel']:
            ser = self.sers[button_led_map.map_arrays['micro'][led - 1]]
            cmd = bytearray([0xE8, 0x03, 0x40])
            value = int(hex(int(4))[2:], 16)
            cmd.append(value)
            cmd.append(button_led_map.map_arrays['logical'][led - 1])
            cmd.append(0x00)
            cmd.append(0xEE)
            cmd[-2] = calculate_checksum(cmd)
            ser.write(cmd)
            time.sleep(.01)
            cmd[3] = int(hex(int(1))[2:], 16)
            cmd[-2] = calculate_checksum(cmd)
            ser.write(cmd)
            time.sleep(.01)

if __name__ == '__main__':
    t = StartUpTester()
    t.run_startup()