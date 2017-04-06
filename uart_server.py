"""
FILE:   uart_server.py
DESCRIPTION: Uart server methods for handling the reads
on the incoming uart data. This is non-blocking by using the
select statement within listen_serial. By definition, this select
statement allows a serial connection to only be read when there
is data in the port to be read.

Commented lines are alternative methods for non-blocking threaded
code. Not used currently, but possibly later if needed.

WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
2/1/17          JDP                original
"""
import serial
import select
# import Adafruit_GPIO as GPIO
import socket
from message_utils import handle_unsolicited

MICRO_ACK = 'E8018069EE'

def calculate_checksum(micro_cmd):
    sum = 0
    ba = bytearray(micro_cmd)

    for i in range(len(ba[:-2])):
        print ba[i]
        sum += ba[i]
    return sum % 0x100

def serial_worker():
    """
    Serial thread which listens for incoming
    unsolicted messages
    @return: 
    """
    ser = serial.Serial('/dev/ttyO4', 115200)
    print 'setting up serial'

    while True:
        incoming_command = ""
        start_char = ser.read(1)
        incoming_command += start_char

        if ord(start_char) == 0xe8:
            length = ser.read(1)
            incoming_command += length
            for i in range(ord(length)):
                cmd_byte = ser.read(1)
                incoming_command += cmd_byte
            checksum = ser.read(1)
            print ord(checksum)
            chk = calculate_checksum(incoming_command)
            print chk
            if chk == checksum:
                incoming_command += checksum
                stop_char = ser.read(1)
                incoming_command += stop_char
                print ":".join("{:02x}".format(ord(c)) for c in incoming_command)
                ser.write(MICRO_ACK)


class SerialReceiveHandler:

    def __init__(self, baudrate=115200, timeout=None):
        """
        Initialize list of uart ports and setup serial
        listeners for incoming messages
        @param baudrate: baudrate, default 115200
        @param timeout: serial timeout, default None
        """
        self.uarts = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
        self.timeout = timeout
        serial_listeners = self.setup_listeners()
        # self.TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.TCP_CLIENT.connect((DSP_SERVER_IP, DSP_SERVER_PORT))

        '''
        Possible other functions for threading serial
        connections instead of using Select:

        self.setup_threads(serial_listeners)
        '''

        self.listen_serial(serial_listeners)

    def setup_listeners(self):
        """
        Creates array of serial fd handles for
        each of the uarts on the bb
        @return: array of serial handles
        """
        sers = []
        for uart in self.uarts:
            try:
                ser = serial.Serial(uart, baudrate=115200, timeout=self.timeout)
                sers.append(ser)
            except serial.SerialException as e:
                print 'Serial Exception Thrown on connection: ', e
                continue
        return sers

    def listen_serial(self, sers):
        """
        While loop for incoming serial messages
        to be handed when they are able to be handled.
        Select statement makes this non-blocking reads of
        serial connections
        @param sers: array of serial handlers
        @return: None
        """
        while 1:
            readable, writable, exceptional = select.select(sers, [], sers)
            for serial_connection in readable:
                #if serial_connection.inWaiting() > 0:
                    try:
                        incoming_command = ""
                        while True:
                            var = serial_connection.read(1)
                            print ord(var)

                            if ord(var) == 0xee:
                                incoming_command += var
                                print ":".join("{:02x}".format(ord(c)) for c in incoming_command)
                                break
                            else:
                                incoming_command += var

                        # msg = handle_unsolicited(incoming_command)
                        serial_connection.write(bytearray.fromhex(MICRO_ACK))
                        # self.TCP_CLIENT.sendall(msg)

                    except serial.SerialException as e:
                        print 'Cannot read line, Serial Exception Thrown:  ', e
                        continue
    '''
    def setup_threads(self, sers):
        for ser in sers:
          thread = Thread(target=self.threaded_serial, args=(ser,))
          thread.start()

    def threaded_serial(self, ser):
        while True:
          if ser.inWaiting()>0:
            var = ser.readline()
            #print 'incoming: ', ser.port, ' ', var
            self.handle(var)
    '''


if __name__ == '__main__':
    SerialReceiveHandler()
    # serial_worker()
    # print ":".join("{:02x}".format(ord(c)) for c in serial_worker())
    # ser = serial.Serial('/dev/ttyO1', 115200)
    # incoming_command = ""
    # while True:
    #     var = ser.read(1)
    #     if ord(var) == 0xee:
    #         incoming_command += var
    #         print ":".join("{:02x}".format(ord(c)) for c in incoming_command)
    #         ser.write(incoming_command)
    #     else:
    #         incoming_command += var

