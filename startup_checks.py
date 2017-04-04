import serial
import time

DEBUG = False
MICRO_STATUS = 'E80231001BEE'
ALL_LEDS = 'E80240F822EE'
MICRO_ACK = 'E8018069EE'

class StartUpTester:
    def __init__(self):
        #self.uart_ports = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
        self.uart_ports = ['/dev/ttyO1', '/dev/ttyO1', '/dev/ttyO1', '/dev/ttyO1']
        self.sers = []
        self.baudrate = 115200
        self.timeout = None
        self.setup_sers()

    def setup_sers(self):
        for uart in self.uart_ports:
            self.sers.append(serial.Serial(uart, self.baudrate))

    def calculate_checksum(self, micro_cmd):
        sum = 0
        for i in range(len(micro_cmd) - 2):
            sum += micro_cmd[i]

        return sum % 0x100

    def read_serial(self, ser):
        ba = bytearray()
        checksum = 0
        start_char = ser.read(1)
        ba.append(start_char)

        if ord(start_char) == 0xe8:
            length = ser.read(1)
            ba.append(length)
            for i in range(ord(length)):
                cmd_byte = ser.read(1)
                ba.append(cmd_byte)
            checksum = ser.read(1)
            ba.append(checksum)
            stop_char = ser.read(1)
            ba.append(stop_char)

        c = self.calculate_checksum(ba)
        if DEBUG:
            print 'Checksum: ', c, ord(checksum)
            print 'Message: ', str(ba)

        if c == ord(checksum) and str(ba) == bytearray.fromhex(MICRO_ACK):
            return 1
        else:
            return 0

    def check_micros(self):
        micro_up = 0
        for ser in self.sers:
            if DEBUG:
                print 'Current serial connection:',ser
            ser.write(bytearray.fromhex(MICRO_STATUS))
            micro_up += self.read_serial(ser)
            time.sleep(.5)
        if micro_up == 4:
            return True

    def start_lightup(self):
        micro_acks = 0
        for ser in self.sers:
            if DEBUG:
                print 'Current serial connections:',ser
            ser.write(bytearray.fromhex(ALL_LEDS))
            micro_acks += self.read_serial(ser)
            time.sleep(.5)
        if micro_acks == 4:
            return True

    def run_startup(self):
        print 'Checking micro connections..'
        if self.check_micros():
            print 'Done\nStarting lightup sequence..'
            if self.start_lightup():
                print 'Done'

if __name__ == '__main__':
    s = StartUpTester()
    s.run_startup()

