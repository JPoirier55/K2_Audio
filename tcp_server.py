"""
FILE:   tcp_server.py
DESCRIPTION: TCP server module which runs on boot and handles incoming
messages from the DSP through TCP connection.

Can be run through the command line with arguments for HOST (--h) and PORT (--p)
to start the server running locally or through dev env.
Currently only supports IPv4

WRITTEN BY: Jake Poirier

"""

import json
from message_utils import MessageHandler, error_response, handle_unsolicited
from button_led_map import map_arrays
import argparse
import threading
from threading import Lock
import serial
import select
import Queue
import socket
import time
from globals import *


uart_lock1 = Lock()
uart_lock2 = Lock()
uart_lock4 = Lock()
uart_lock5 = Lock()

LOCKS = {'/dev/ttyO1': uart_lock1,
         '/dev/ttyO2': uart_lock2,
         '/dev/ttyO4': uart_lock4,
         '/dev/ttyO5': uart_lock5}

xLOCKS = {'/dev/ttyO1': uart_lock1}

READY = False

# TODO: DOCUMENT METHODS!!!


class StartUpTester:
    def __init__(self):
        # self.uart_ports = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
        self.uart_ports = UART_PORTS
        self.sers = []
        self.baudrate = 115200
        self.timeout = None
        self.setup_sers()

    def setup_sers(self):
        """
        Create list of serial file descriptors
        needed for running the initial start sequence
        @return: None
        """
        for uart in self.uart_ports:
            self.sers.append(serial.Serial(uart, self.baudrate))

    def calculate_checksum(self, micro_cmd):
        """
        Calculate checksum from micro_cmd bytearray
        object. Same method as in message_utils,
        but used here as well.
        @param micro_cmd: incoming micro command bytearray
        @return: checksum integer
        """
        sum = 0
        for i in range(len(micro_cmd) - 2):
            sum += micro_cmd[i]
        return sum % 0x100

    def read_serial(self, ser):
        """
        Method to read incoming message from
        micro after sending message
        @param ser: serial object
        @return: 1 - checksum correct and ack received
                 2 - either checksum or ack not correct/received
        """
        ba, checksum = read_serial_generic(ser)

        c = self.calculate_checksum(ba)

        if c == ord(checksum) and str(ba) == MICRO_ACK:
            return 1
        else:
            return 0

    def send_command(self, micro_cmd):
        """
        Send micro command for initial startup
        sequence, and read incoming ack
        @param message: outgoing micro command
        @return: True - If all four acks have been received
                 False - If less than four received
        """
        micro_ack = 0
        for ser in self.sers:
            if DEBUG:
                print 'Current serial connection:', ser
            ser.write(bytearray.fromhex(micro_cmd))
            micro_ack += self.read_serial(ser)
            time.sleep(.5)
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
        print 'Checking micro connections..'
        if self.send_command(MICRO_STATUS):
            print 'Done\nStarting lightup sequence..'
            if self.send_command(ALL_LEDS):
                print 'Done'
                time.sleep(5)
                print 'Stopping lighting sequence..'
                self.send_command(ALL_LEDS_OFF)
                return True
        return False

    def run_blinky_sequence(self):
        """
        Iterate through LEDs on control board
        to turn on in the order 1-2-3-...202-203
        Each one has a wait of .1 seconds between
        turning on
        @return: None
        """
        for led in map_arrays['panel']:
            ser = self.sers[map_arrays['micro'][led-1]]
            cmd = 'E8024001{0:0{1}X}00EE'.format(map_arrays['logical'][led-1], 2)
            chk = self.calculate_checksum(bytearray.fromhex(cmd))
            cmd = cmd[:-4] + str(hex(chk)[2:]) + cmd[-2:]
            cmd = bytearray.fromhex(cmd)

            ser.write(cmd)
            time.sleep(.01)


def startup_worker():
    """
    Thread which runs the startup sequence 
    until the READY global variable is False.
    This sequence is essentially waiting for 
    the DSP to send a status update message, 
    when its time to reconnect. This thread
    will run until that message is sent, and
    will be killed when it is sent.
    @return: None, thread closed
    """
    s = StartUpTester()
    while True:
        if s.run_startup():
            while True:
                if not READY:
                    if DEBUG:
                        print 'Ready: ', READY
                    s.run_blinky_sequence()
                    s.send_command(ALL_LEDS_OFF)
                else:
                    if DEBUG:
                        print 'Ready: ', READY
                        print 'Stopping startup sequence'
                    break
            break


def read_serial_generic(ser):
    checksum = 0
    ba = bytearray()
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
    return ba, checksum


class SerialSendHandler:
    def __init__(self, port, baudrate=115200, timeout=None):
        """
        Init baudrate and timeout for serial
        @param baudrate: baudrate, default 115200
        @param timeout: timeout, default None
        """
        self.baudrate = baudrate
        self.timeout = timeout
        self.port = port
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)

    def read_uart(self):
        line = self.ser.readline()
        return line

    def flush_input(self):
        self.ser.flushInput()

    def send_uart(self, command):
        """
        Connect to serial connection and send command.
        Then close serial connection
        @param command: 
        @return: None
        """
        print 'sending: ', command, " ", self.port
        print ":".join("{:02x}".format(c) for c in command)
        self.ser.write(command)

    def close(self):
        self.ser.close()


def serial_handle(uart_command, uart_port):
    """
    Generic method which handles the serial locking
    and conversion to be sent, also checks the recv
    ack from the micro to verify its correct
    @param uart_command: command from micro
    @param uart_port: port command comes on
    @return:
    """
    ser = serial.Serial('/dev/ttyO1', 115200)
    command = bytearray.fromhex(uart_command)

    if DEBUG:
        print command, uart_port

    ser.write(command)
    ser.close()
    return True

    # ack = False
    # while True:
    #     if LOCKS[uart_port].acquire():
    #         try:
    #             # ser = SerialSendHandler(uart_port)
    #             # ser.flush_input()
    #             ser = serial.Serial('/dev/ttyO1', 115200)
    #             command = bytearray.fromhex(uart_command)
    #
    #             if DEBUG:
    #                 print command, uart_port
    #
    #             ser.write(command)
    #             micro_response = ""
    #             while True:
    #                 var = ser.read(1)
    #                 if ord(var) == 0xee:
    #                     micro_response += var
    #                     # print ":".join("{:02x}".format(ord(c)) for c in micro_response)
    #                     # TODO: check ack here
    #                     break
    #                 else:
    #                     micro_response += var
    #             ser.close()
    #         finally:
    #             LOCKS[uart_port].release()
    #         break
    # return ack


class DataHandler:

    def __init__(self):
        pass

    def handle_all_msg(self, uart_command):
        """
        Handle messages that go to all uarts
        @param uart_command: 
        @return: 
        """
        ack_num = 0
        for uart_port in UART_PORTS:
            while True:
                if (serial_handle(uart_command, uart_port)):
                    ack_num += 1
                break
        if ack_num == 4:
            return True

        else:
            return False

    def handle_arr_msg(self, uart_command):
        """
        Handle messages that come in as arrays
        @param uart_command: 
        @return: 
        """
        ack_num = 0

        count = 0
        for uart_port, single_uart_command in uart_command.iteritems():
            count += 1
            if len(single_uart_command) > 0:
                single_command = json.dumps(single_uart_command).strip('"')
                if serial_handle(single_command, uart_port):
                    ack_num += 1
        if ack_num == count:
            return True
        else:
            return False

    def handle_other_msg(self, uart_command, uart_port):
        """
        Handle all other messages such as single leds,
        firmware or status messages
        @param uart_command: 
        @param uart_port: 
        @return: 
        """

        if(serial_handle(uart_command, uart_port)):
            return True
        else:
            return False

    def allocate(self, incoming_data):
        """
        Allocate incoming data to whatever micro command 
        it is supposed to be 
        @param incoming_data: 
        @return: None
        """
        try:
            json_data = json.loads(incoming_data.replace(",}", "}"), encoding='utf8')
        except Exception as e:
            return error_response(0)[0]
        response = ""
        if all(key in json_data for key in
               ("action", "category", "component", "component_id", "value")):
            msg = MessageHandler(json_data)
            response, (uart_command, uart_port) = msg.process_command()

            if DEBUG:
                print 'response:', response
                print 'uart com :', uart_command
                print 'uart port: ', uart_port

            if uart_port == "ALL":
                if self.handle_all_msg(uart_command):
                    return response

            elif uart_port == "ARRAY":
                if self.handle_arr_msg(uart_command):
                    return response

            else:
                if self.handle_other_msg(uart_command, uart_port):
                    return response

        else:
            if DEBUG:
                print 'Returning with failure'
            return error_response(0)[0]


def tcp_handler(sock):
    """
    Main tcp handler which cycles through 
    readable file descriptors to check for 
    any incoming tcp packets. Allows only 5 
    readable connections, then drops the ones
    that aren't used. There is a single socket
    as the main file descriptor, followed by 
    other connections, which get culled when
    more than 5.
    @param sock: 
    @return: None
    """
    inputs = [sock]
    outputs = []
    message_queues = {}
    data_handler = DataHandler()
    global READY

    try:
        # TODO: Strip this down into something a little more elegant
        while inputs:

            if len(inputs) > 5:
                for t in range(1, len(inputs)-1):
                    inputs[t].close()
                inputs = [inputs[0], inputs[len(inputs)-1]]

            readable, writable, exceptional = select.select(inputs, [], [sock], 1)
            for s in readable:
                if s is sock:
                    connection, client_address = s.accept()
                    if DEBUG:
                        print 'Connect', client_address
                    connection.setblocking(0)
                    inputs.append(connection)

                    message_queues[connection] = Queue.Queue()
                else:
                    data = s.recv(1024)

                    if data:
                        if DEBUG:
                            print 'Data:', data
                        # add to queue if response
                        # TODO: check for status message as first boot up, then set ready=true
                        READY = True
                        message_queues[s].put(data)
                        response = data_handler.allocate(data)
                        if DEBUG:
                            print 'return response to ', client_address, '  ', response
                        s.sendall(json.dumps(response))

                        if s not in outputs:
                            outputs.append(s)
                    else:
                        if DEBUG:
                            print 'Closing:', s
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        # remove from queue
                        del message_queues[s]

    except Exception as e:
        print e
        return


class SerialHandler:
    def __init__(self):
        self.uart_ports = UART_PORTS
        self.ser = None
        self.gpio_fds = []
        self.sers = []
        self.setup()
        self.TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_CLIENT.connect((DSP_SERVER_IP, DSP_SERVER_PORT))

    def setup(self):
        if DEBUG:
            print 'Setting up Serial connections'
        for uart in self.uart_ports:
            new_ser = serial.Serial(uart, 115200)
            self.sers.append(new_ser)

    def send_tcp(self, unsol_msg, uart_port):

        tcp_message = handle_unsolicited(unsol_msg, uart_port)
        if DEBUG:
            print 'TCP Message: ', tcp_message
        self.TCP_CLIENT.send(json.dumps(tcp_message))
        return True

    def calculate_checksum(self, micro_cmd):
        sum = 0
        for i in range(len(micro_cmd) - 2):
            sum += micro_cmd[i]

        return sum % 0x100

    def handle_message(self):
        if DEBUG:
            print "Serial connection: ", self.ser
        try:
            # TODO: use except to catch issues, return error message
            ba, checksum = read_serial_generic(self.ser)

            c = self.calculate_checksum(ba)
            if DEBUG:
                print 'Checksum: ', c, ord(checksum)
            if c == ord(checksum):
                print 'tcp time'
                if self.send_tcp(str(ba), self.ser.port):
                    self.ser.write(MICRO_ACK)
                else:
                    self.ser.write(MICRO_ERR)
            else:
                # TODO: catch this error and respond wtih error message
                print 'bad checksum'
        except Exception, e:
            print e

    def handle_locks(self, port_index):
        while True:
            if LOCKS[self.uart_ports[port_index]].acquire():
                try:
                    if DEBUG:
                        print 'Serial lock acquired'
                    self.ser = self.sers[port_index]
                    self.ser.flushInput()
                    GPIO.output("USR{0}".format(port_index), GPIO.HIGH)
                    self.handle_message()

                finally:
                    LOCKS[self.uart_ports[port_index]].release()
                    GPIO.output("USR{0}".format(port_index), GPIO.LOW)
                    if DEBUG:
                        print 'Serial lock released'
                    break

    def serial_worker(self):
        """
        Serial thread which listens for incoming
        unsolicted messages
        @return: 
        """
        vals = []
        while True:

            for gpio in RTS_GPIOS:
                open_file = open(gpio)
                self.gpio_fds.append(open_file)

            for gpio_edge_fd in GPIO_EDGE_FDS:
                fd = open(gpio_edge_fd, 'w')
                fd.write("both")

            for fd in self.gpio_fds:
                vals.append(fd.read())

            readable, writable, exceptional = select.select([], [], self.gpio_fds, 5)
            for e in exceptional:
                if e == self.gpio_fds[0]:
                    if int(vals[0]) == 1:
                        self.handle_locks(0)

                elif e == self.gpio_fds[1]:
                    if int(vals[1]) == 1:
                        self.handle_locks(1)

                elif e == self.gpio_fds[2]:
                    if int(vals[2]) == 1:
                        self.handle_locks(2)

                elif e == self.gpio_fds[3]:
                    if int(vals[3]) == 1:
                        self.handle_locks(3)

            vals = []
            self.gpio_fds = []


if __name__ == "__main__":

    # TODO: Make this its own CLI and create global for READY variable that gets checked in startup_checks
    parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST, PORT = args.h, args.p

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serial_handler = SerialHandler()

    serial_thread = threading.Thread(target=serial_handler.serial_worker)
    serial_thread.daemon = True
    serial_thread.start()

    startup_thread = threading.Thread(target=startup_worker)
    startup_thread.daemon = True
    startup_thread.start()

    server_address = (HOST, int(PORT))
    print 'Starting server on:', server_address

    sock.bind(server_address)
    sock.setblocking(0)
    sock.listen(1)

    # while True:
    tcp_handler(sock)
