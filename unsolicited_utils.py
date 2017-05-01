"""
FILE:   unsolicited_utils.py

DESCRIPTION: Module to handle all unsolicited translations between
micro commands nad tcp packets set to dsp

WRITTEN BY: Jake Poirier

"""
from globals import *
from button_led_map import *
from command_map import *
DEBUG = True


def calculate_checksum_bytes(micro_cmd):
    """
    Calculates checksum of incoming
    micro command that is from an 
    unsolicited command and is of the 
    form byte array

    @param micro_cmd: 
    @return: checksum
    """
    sum = 0
    for i in range(len(micro_cmd) - 2):
        sum += micro_cmd[i]
    return sum % 0x100


class UnsolicitedHandler:
    """
    Handler for all unsolicited commands from micro
    """
    def __init__(self):
        self.micro_command = None
        self.uart_port = None

    def allocate_command(self, micro_command, uart_port):
        """
        Looks at third byte of micro_command to see what 
        command has been sent from micro, and handles
        accordingly.
        
        @param micro_command: incoming command bytearray from micro
        @param uart_port: port command coming in on
        @return: True - message handl
        """
        self.micro_command = micro_command
        self.uart_port = uart_port

        cmd = self.micro_command[2]
        checksum = self.micro_command[-2]

        try:
            cs = calculate_checksum_bytes(self.micro_command)
        except:
            return None

        if checksum == cs:
            if cmd == 0x10:
                return self.handle_switch_press()
            elif cmd == 0x11:
                return self.handle_encoder_change()
            elif cmd == 0x90:
                return self.handle_exception()
            else:
                return None

    def handle_switch_press(self):
        """
        Handle unsolicited switch presses from micro,
        converts logical id from micro into panel id
        for dsp
        
        @return: TCP JSON command 
        """
        micro_button_number = self.micro_command[3]
        # if DEBUG:
        #     print ":".join("{:02x}".format(c) for c in self.micro_command)

        button_index = micro_array[self.uart_port]['logical'].index(micro_button_number)
        panel_button_number = micro_array[self.uart_port]['panel'][button_index]

        value = self.micro_command[4]
        tcp_command = {'category': 'BTN',
                       'component': 'SW',
                       'component_id': str(panel_button_number),
                       'action': '=',
                       'value': str(value)}
        return tcp_command

    def handle_encoder_change(self):
        """
        Handles any micro commands from encoder
        and returns tcp json commmand to dsp
        
        @return: TCP JSON command
        """
        value = self.micro_command[3]
        tcp_command = {'category': 'ENC',
                       'component': 'POS',
                       'component_id': '0',
                       'action': '=',
                       'value': str(value)}
        return tcp_command

    def handle_exception(self):
        """
        Handles any unsolicited micro exceptions
        and looks up correct exception id to add
        the description to the tcp json command
        
        @return: TCP JSON command
        """
        value = self.micro_command[3]
        desc = ""
        for description, byte_code in exception_codes.iteritems():
            if value == byte_code:
                desc = description
        tcp_command = {'category': 'EXCEPTION',
                       'component': '',
                       'component_id': '',
                       'action': '=',
                       'value': str(value),
                       'description': desc}
        return tcp_command
