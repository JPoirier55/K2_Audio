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
import socket
import time
import logging
import os
import datetime
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

if DEBUG:
    READY = True
else:
    READY = False


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

    def read_serial(self, ser):
        """
        Method to read incoming message from
        micro after sending message
        @param ser: serial object
        @return: 1 - checksum correct and ack received
                 2 - either checksum or ack not correct/received
        """
        ba, checksum = read_serial_generic(ser)

        c = calculate_checksum(ba)

        if c == ord(checksum) and str(ba) == MICRO_ACK:
            return 1
        else:
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
            if not READY:
                ser = self.sers[map_arrays['micro'][led-1]]
                cmd = 'E8024001{0:0{1}X}00EE'.format(map_arrays['logical'][led-1], 2)
                chk = calculate_checksum(bytearray.fromhex(cmd))
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


def calculate_checksum(micro_cmd):
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
    if len(ba) == 0:
        return None, None
    return ba, checksum


class SerialSendHandler:
    """
    Handles all serial connections, controls serial locks for each UART port
    """
    def __init__(self, baudrate=115200, timeout=None):
        """
        Init baudrate and timeout for serial
        @param baudrate: baudrate, default 115200
        @param timeout: timeout, default None
        """
        self.baudrate = baudrate
        self.timeout = timeout

    def serial_handle(self, uart_command, uart_port):
        """
        Generic method which handles the serial locking
        and conversion to be sent, also checks the recv
        ack from the micro to verify its correct
        @param uart_command: command from micro
        @param uart_port: port command comes on
        @return:
        """
        uart_response = None
        checksum = None
        try:
            ack = False
            while True:
                # Wait until lock is accessible, then acquire
                if LOCKS[uart_port].acquire():
                    try:
                        self.ser = serial.Serial(uart_port, self.baudrate)
                        self.ser.flushInput()

                        # TODO: start from here and make everything bytearrays
                        command = bytearray.fromhex(uart_command)
                        if DEBUG:
                            print command, uart_port

                        print 'command'
                        print ":".join("{:02x}".format(c) for c in command)

                        self.ser.write(command)

                        uart_response, checksum = read_serial_generic(self.ser)
                        print 'response'
                        print ":".join("{:02x}".format(c) for c in uart_response)
                        print checksum

                    finally:
                        LOCKS[uart_port].release()
                    break

            if calculate_checksum(uart_response) == ord(checksum):
                return uart_response
            else:
                return None
        except serial.SerialException, e:
            logging.exception("{0} - Cannot write serial message".format(datetime.datetime.now()))
            return None


class DataHandler:
    """
    Handles all outgoing data for micro commands, and does checks for responses from micros as ACKs
    """
    def __init__(self):
        """
        Init serial handler
        """
        self.serial_handler = SerialSendHandler()

    def handle_all_msg(self, uart_command):
        """
        Handle messages that go to all micros/ports
        Checks to see if all ACKs are received 
        
        @param uart_command: incoming command to be sent to all micros
        @return: True - ACK, False - NACK
        """
        ack_num = 0
        for uart_port in UART_PORTS:
            while True:
                if (self.serial_handler.serial_handle(uart_command, uart_port)):
                    ack_num += 1
                break
        if ack_num == 4:
            return True
        else:
            return False

    def handle_arr_msg(self, uart_command):
        """
        Handle messages that come in as arrays
        and send them to corresponding micro/port 
        for each message
        Checks to see if all ACKs are received with
        count vs ack_num 
        
        @param uart_command: Incoming dict with {'port':'command'} format 
        @return: True - ACK, False - NACK
        """
        ack_num = 0

        count = 0
        for uart_port, uart_commands in uart_command.iteritems():
            count += 1
            for single_uart_command in uart_commands:
                if len(single_uart_command) > 0:
                    single_command = json.dumps(single_uart_command).strip('"')
                    if self.serial_handler.serial_handle(single_command, uart_port):
                        ack_num += 1
        if ack_num == count:
            for uart_port, uart_commands in uart_command.iteritems():
                count += 1

                if self.serial_handler.serial_handle(single_command, uart_port):
                    ack_num += 1
            return True
        else:
            return False

    def handle_other_msg(self, uart_command, uart_port):
        """
        Handle all other messages such as single leds,
        firmware or status messages
        
        @param uart_command: Incoming uart command
        @param uart_port: Corresponding port for command
        @return: True - ACK, False - NACK
        """
        if(self.serial_handler.serial_handle(uart_command, uart_port)):
            return True
        else:
            return False

    # def handle_set_msg(self):

    def allocate(self, json_data):
        """
        Allocate incoming data to corresponding function
        for further processing and micro messaging.
        
        Options include commands for:
        
        ERROR - Some error occurred while processing or from micro
        ALL - Command will be sent to all micros, and expect 4 acks
        ARRAY - Command will be sent to corresponding micros 
        Other - Command falls into other category, including single LED/SW commands
        
        @param json_data: Incoming json data from TCP handler
        @return: Response to be sent back through TCP to dsp
        """
        response = ""
        try:
            # Ensure json is of correct format
            if all(key in json_data for key in
                   ("action", "category", "component", "component_id", "value")):
                message_handler = MessageHandler(json_data)
                category = json_data['category']
                action = json_data['action']
                cid = json_data['component_id']
                response = json_data

                if category == "CFG" and (action == "SET" or action == "GET"):
                    uart_command, uart_port = message_handler.run_config_cmd()
                    uart_response = self.serial_handler.serial_handle(uart_command, uart_port)
                    if uart_response is not None:
                        if action == "SET":
                            if uart_response == MICRO_ACK:
                                response['action'] = '='
                                return response
                        else:
                            response['value'] = str(uart_response[3])
                            response['action'] = '='
                            return response
                    else:
                        return error_response(1)[0]

                elif category == "STS":
                    ack_num = 0
                    uart_command, uart_port = message_handler.run_status_cmd()
                    uart_responses = []
                    if uart_port == 'ALL':
                        for port in UART_PORTS:
                            uart_responses.append(self.serial_handler.serial_handle(uart_command, port))
                    if len(uart_responses) > 0:
                        if cid == "STS":
                            for uart_response in uart_responses:
                                if uart_response == MICRO_ACK:
                                    ack_num += 1
                            if ack_num == 4:
                                response['value'] = '1'
                                response['action'] = '='
                                return response
                        if cid == "FW":
                            if len(set([str(uart_str) for uart_str in uart_responses])) <= 1:
                                response['value'] = FIRMWARE[str(uart_responses[0][3])]
                                response['action'] = '='
                                return response
                            else:
                                response['value'] = 'xxx'
                                response['action'] = '='
                                return response
                    else:
                        return error_response(1)[0]
                elif category == "BTN":
                    uart_command, uart_port = message_handler.run_button_cmd()
                    if uart_port == "ALL":
                        uart_responses = []
                        for port in UART_PORTS:
                            uart_responses.append(self.serial_handler.serial_handle(uart_command, port))

                    elif uart_port == "ARRAY":
                        if self.handle_arr_msg(uart_command):
                            return response

                    elif uart_port in UART_PORTS:
                        if self.handle_other_msg(uart_command, uart_port):
                            return response
                    else:
                        return response
                # elif category == "ENC":
                #     response, (uart_command, uart_port) = message_handler.run_encoder_cmd()
                else:
                    return error_response(1)[0]

                # # Create command and allocate port for serial sending
                # response, (uart_command, uart_port) = msg.process_command()

                # if response['category'] == 'ERROR':
                #     return error_response(2)[0]

                # if DEBUG:
                #     print 'response:', response
                #     print 'uart com :', uart_command
                #     print 'uart port: ', uart_port

            else:
                if DEBUG:
                    print 'Returning with failure'
                return error_response(0)[0]

        except TypeError, e:
            print e
            print'ERRO2'
            logging.exception("{0} - Failed reading and allocating micro message".format(datetime.datetime.now()))
            return error_response(0)[0]


def tcp_handler(sock):
    """
    Main tcp handler which cycles through 
    readable socket file descriptors to check for 
    any incoming tcp packets. Allows only 5 
    readable connections, then drops the ones
    that aren't used. There is a single socket
    as the main file descriptor, followed by 
    other connections, which get culled when
    more than 5.
    
    @param sock: main socket connection
    @return: None
    """
    # Index 1 of inputs is always main socket connection
    inputs = [sock]
    outputs = []
    data_handler = DataHandler()
    global READY
    client_address = ''

    try:
        while inputs:
            # Cut out idle socket connections when there are more than 5
            if len(inputs) > 5:
                for t in range(1, len(inputs)-1):
                    # Close extra idle connections
                    inputs[t].close()
                # Remove extra idle connections, keep index 1 (main socket) and last index (current socket)
                inputs = [inputs[0], inputs[len(inputs)-1]]

            readable, writable, exceptional = select.select(inputs, [], [sock], 1)
            for s in readable:
                if s is sock:
                    connection, client_address = s.accept()
                    if DEBUG:
                        print 'Connect', client_address
                    connection.setblocking(0)
                    inputs.append(connection)
                else:
                    data = s.recv(1024)
                    if data:
                        try:
                            json_data = json.loads(data.replace(",}", "}"), encoding='utf8')
                        except Exception as e:
                            return error_response(0)[0]

                        # Check for basic status command to kick out of startup sequence
                        if json_data['category'] == 'STS' and json_data['component'] == 'SYS':
                            READY = True

                        if READY:
                            response = data_handler.allocate(json_data)

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

    except socket.error, e:
        print'ERROR'
        logging.exception("{0} - Failed to read data from socket".format(datetime.datetime.now()))
        return


class SerialReceiveHandler:
    """
    Handles all incoming unsolicited messages from UARTS, controls RTS/CTS GPIOs to handle unsolicited
    """
    def __init__(self):
        """
        Init all uart ports to listen on, init TCP client for connecting to DSP server
        """
        self.uart_ports = UART_PORTS
        self.ser = None
        self.gpio_fds = []
        self.sers = []
        self.setup()
        self.TCP_CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_CLIENT.connect((DSP_SERVER_IP, DSP_SERVER_PORT))

    def setup(self):
        """
        Create new serial objects to be used to
        read incoming serial messages, append
        them to an array
        @return: None
        """
        if DEBUG:
            print 'Setting up Serial connections'
        for uart in self.uart_ports:
            new_ser = serial.Serial(uart, 115200)
            self.sers.append(new_ser)

    def send_tcp(self, unsol_msg, uart_port):
        """
        Send TCP through to DSP with whatever
        the micro command translates to. This is 
        generally an unsolicited message
        @param unsol_msg: incoming message from micro
        @param uart_port: port being read from
        @return: True if sent, False if not
        """
        tcp_message = handle_unsolicited(unsol_msg, uart_port)
        if DEBUG:
            print 'TCP Message: ', tcp_message
        try:
            self.TCP_CLIENT.send(json.dumps(tcp_message))
        except socket.error, e:
            logging.exception("{0} - Failed to send TCP message".format(datetime.datetime.now()))
            return False
        return True

    def calculate_checksum(self, micro_cmd):
        """
        Class method for handling checksum 
        calculation for micro commands
        @param micro_cmd: incoming command
        @return: sum of the checksum mod 0x100 
        to keep it within a byte
        """
        sum = 0
        for i in range(len(micro_cmd) - 2):
            sum += micro_cmd[i]

        return sum % 0x100

    def handle_message(self):
        """
        Reads message and handles checking for
        correct checksum and returns an error
        or an acknowledgement depending on if 
        the incoming message was good. Sends out tcp
        message if okay, error back to micro if not.
        @return: None
        """
        if DEBUG:
            print "Serial connection: ", self.ser
        try:
            # TODO: use except to catch issues, return error message
            ba, checksum = read_serial_generic(self.ser)
            if ba is not None:
                c = self.calculate_checksum(ba)
                if DEBUG:
                    print 'Checksum: ', c, ord(checksum)
                if c == ord(checksum):
                    if self.send_tcp(str(ba), self.ser.port):
                        self.ser.write(MICRO_ACK)
                    else:
                        self.ser.write(MICRO_ERR)
                else:
                    self.ser.write(MICRO_ERR)
        except serial.SerialException:
            logging.exception("{0} - Cannot read incoming serial message".format(datetime.datetime.now))

    def handle_locks(self, port_index):
        """
        Checks and acquires locks for whatever port 
        the incoming message will come in on. The 
        RTS which has been flagged will be the port
        index and will follow through to set correct
        serial object and CTS flag
        @param port_index: incoming RTS index
        @return: None
        """
        while True:
            if LOCKS[self.uart_ports[port_index]].acquire():
                try:
                    if DEBUG:
                        print 'Serial lock acquired'
                        print 'PORT INDEX', port_index
                        print CTS_GPIOS[port_index]
                    self.ser = self.sers[port_index]
                    self.ser.flushInput()
                    GPIO.output(CTS_GPIOS[port_index], GPIO.HIGH)
                    self.handle_message()

                finally:
                    LOCKS[self.uart_ports[port_index]].release()
                    GPIO.output(CTS_GPIOS[port_index], GPIO.LOW)
                    if DEBUG:
                        print 'Serial lock released'
                    break

    def serial_worker(self):
        """
        Serial thread which listens for incoming
        unsolicted messages. Depending on the incoming
        gpio that is read, the file descriptor will 
        trigger and set the port index used in 
        handle_locks. The select exceptional statement
        won't get called until one of the file descriptors
        has changed, aka RTS has been flagged.
        @return: None 
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
                        print self.gpio_fds[0]
                        self.handle_locks(0)

                elif e == self.gpio_fds[1]:
                    if int(vals[1]) == 1:
                        print self.gpio_fds[0]
                        self.handle_locks(1)

                elif e == self.gpio_fds[2]:
                    if int(vals[2]) == 1:
                        print self.gpio_fds[0]
                        self.handle_locks(2)

                elif e == self.gpio_fds[3]:
                    if int(vals[3]) == 1:
                        print self.gpio_fds[0]
                        self.handle_locks(3)

            vals = []
            self.gpio_fds = []


def check_logfile_size():
    """
    Clear logfile if the size is greater than
    1MB
    This assumes the log file will be checked, as
    well as used. This could be used for debugging 
    during development or triage during use.
    
    @return: None 
    """
    logfile = os.stat('K2_logging.log')
    size = logfile.st_size
    if size > 1000000:
        with open('K2_logging.log', 'w'):
            pass


if __name__ == "__main__":
    logging.basicConfig(filename='K2_logging.log', level=logging.DEBUG)
    check_logfile_size()

    parser = argparse.ArgumentParser(description='Provide port and host for TCP server')
    parser.add_argument('--h', '--HOST', default='0.0.0.0', help='Host ipv4 address (default 0.0.0.0)')
    parser.add_argument('--p', '--PORT', default=65000, help='Port (default 65000)')

    args = parser.parse_args()
    HOST, PORT = args.h, args.p

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serial_handler = SerialReceiveHandler()

    serial_thread = threading.Thread(target=serial_handler.serial_worker)
    serial_thread.daemon = True
    serial_thread.start()

    # startup_thread = threading.Thread(target=startup_worker)
    # startup_thread.daemon = True
    # startup_thread.start()

    server_address = (HOST, int(PORT))
    print 'Starting server on:', server_address

    sock.bind(server_address)
    sock.setblocking(0)
    sock.listen(1)

    tcp_handler(sock)
