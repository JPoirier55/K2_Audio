"""
FILE:   message_utils.py
DESCRIPTION: Set of utility functions used for handling
and processing the messages that come from the DSP and require
manipulation before sending to micros.

WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
1/25/17          JDP                original
"""
import serial
import json
from copy import deepcopy
import time
import status_utils
from button_led_map import map_arrays
from command_map import *
import binascii

FIRMWARE_VERSION = "001"
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']


def send_uart(json_command, uart_port):
    """

    **DEPRECATED**

    Simple uart sending method, possibly deprecated
    in the near future for something more robust
    @param json_command: Incoming json command to be sent
    @param uart_port: Port to send data to
    @return: None
    """
    ser = serial.Serial(uart_port, baudrate=115200, timeout=None)
    ser.write(json.dumps(json_command) + "\r\n")
    time.sleep(.05)
    ser.close()


def error_response(error_id):
    """
    Error handler and builder
    @param error_id: ID of error
    @return: Error response in JSON format
    """
    error_descs = ['Invalid category or component.',
                   'State (parameter) out of range',
                   'Command not understood/syntax invalid.']

    response = {'category': 'ERROR',
                'component': '',
                'component_id': '',
                'action': '=',
                'value': str(error_id),
                'description': error_descs[error_id-1]}

    return response, (None, None)


def translate_uart_port(panel_id):
    """
    Simple method to translate between map_arrays
    and the incoming panel_id for micro number
    @param panel_id: ID from DSP for panel number
    @return: Micro number for panel id
    """
    return UART_PORTS[map_arrays['micro'][panel_id]]


def translate_logical_id(component_id):
    """
    Simple method to translate between panel id and
    logical ids for each micro. Each panel id
    corresponds to a certain id within each set of
    micros and is defined in map_arrays in button_led_map.py
    @param component_id: Incoming id
    @return: Logical ID
    """
    return map_arrays['logical'][(int(component_id))-1]


def translate_cfg_cmd(dsp_command):
    """
    Translated incoming DSP json command to a
    more condensed version to be sent to the micro
    as a possible set of bytes/ascii chars. Will be
    updated for new protocol between bb and micros
    @param command: DSP json command
    @return: new micro command
    """
    comp = dsp_command['component']
    cid = dsp_command['component_id']
    action = dsp_command['action']
    value = dsp_command['value']

    if comp == 'RTE' and cid == 'SLO' and action == 'SET':
        command = command_dict['set_led_slow_rate']
    elif comp == 'RTE' and cid == 'SLO' and action == 'GET':
        command = command_dict['get_led_slow_rate']
    elif comp == 'RTE' and cid == 'FST' and action == 'SET':
        command = command_dict['set_led_fast_rate']
    elif comp == 'RTE' and cid == 'FST' and action == 'GET':
        command = command_dict['get_led_fast_rate']
    elif comp == 'CYC' and cid == 'SLO' and action == 'SET':
        command = command_dict['set_led_slow_dcyc']
    elif comp == 'CYC' and cid == 'SLO' and action == 'GET':
        command = command_dict['get_led_slow_dcyc']
    elif comp == 'CYC' and cid == 'FST' and action == 'SET':
        command = command_dict['set_led_fast_dcyc']
    elif comp == 'CYC' and cid == 'FST' and action == 'GET':
        command = command_dict['get_led_fast_dcyc']
    elif comp == 'ENC' and cid == 'SEN' and action == 'SET':
        command = command_dict['set_enc_sens']
    elif comp == 'ENC' and cid == 'SEN' and action == 'GET':
        command = command_dict['get_enc_sens']
    else:
        return None

    if action == 'GET':
        checksum = 0x00
        parameters = 0x00
    else:
        checksum = 0x00
        parameters = 0x00

    length = 0x00
    micro_cmd = "{0}{1}{2}{3}{4}{5}".format(hex_tostring(start_char), hex_tostring(length), hex_tostring(command),
                                            hex_tostring(parameters), hex_tostring(checksum), hex_tostring(stop_char))
    print micro_cmd
    return micro_cmd


def hex_tostring(hex_num):
    return hex(hex_num)[2:]


def translate_enc_cmd(command):
    """
    Translated incoming DSP json command to a
    more condensed version to be sent to the micro
    as a possible set of bytes/ascii chars. Will be
    updated for new protocol between bb and micros
    @param command: DSP json command
    @return: new micro command
    """
    comp = command['component']
    value = command['value']
    action = command['action']
    cid = command['component_id']

    if comp == 'DIS' and action == 'SET':
        command = command_dict['set_enc_disp']
    elif comp == 'DIS' and action == 'GET':
        command = command_dict['get_enc_disp']
    else:
        return None

    if action == 'GET':
        checksum = 0x00
        parameters = 0x00
    else:
        checksum = 0x00
        parameters = 0x00

    length = 0x00
    micro_cmd = "{0}{1}{2}{3}{4}{5}".format(hex_tostring(start_char), hex_tostring(length), hex_tostring(command),
                                            hex_tostring(parameters), hex_tostring(checksum), hex_tostring(stop_char))
    print micro_cmd
    return micro_cmd


def split_id_array(id_array):
    """
    Yields set of size 16 arrays from individual
    longer array
    @param id_array: incoming >16 len array
    @return: Generator of arrays
    """
    for i in range(0, len(id_array), 16):
        yield id_array[i:i + 16]


def allocate_micro_cmds(command):
    """
    Creates arrays based on the micro that the command
    should be sent to based on the incoming panel id.
    For example, if the array has a set of numbers that
    are all in different micros, this will allocated a
    dict with the micro the message should be sent to.
    This corresponds to the set of arrays in button_led_map.py
    @param command: DSP cmd with array of panel_ids
    @return: Dict with format:

        {'micro_0': [2,3,54,5],
        'micro_1': [6,7,8],
        'micro_2': [8],
        'micro_3': []}
    """
    micro_commands = {'micro_0': [],
                      'micro_1': [],
                      'micro_2': [],
                      'micro_3': []}

    cid_array = command['component_id']
    for cid in cid_array:
        micro_num = map_arrays['micro'][(int(cid))-1]
        micro_commands['micro_' + str(micro_num)].append(cid)
    return micro_commands


def array_to_string(array):
    """
    Simple method to convert array
    to string sep by whitespace
    @param array: incoming array
    @return: string of array
    """
    string = ""
    for element in array:
        string += str(element) + " "
    return string


def button_command_array_handler(command):
    """
    Takes incoming command with an array of BTN IDs
    and splits them into messages that contain a maximum
    of 16 len BTN ids, and put them to the corresponding
    micro based on the logical ids for each id.
    @param command: DSP cmd with array of panel_ids
    @return: Dict with uart ports and strings for micro
    commands
    """
    command_array = {}
    logical_ids = []
    value = command['value']
    command_byte = command_dict['set_led_list']
    micro_cmd = ""
    length = '0'
    checksum = '0'
    parameters = 0x00


    for id in command['component_id']:
        logical_ids.append(translate_logical_id(id))

    cid_arrays = allocate_micro_cmds(command)

    for micro_num, cid_array in cid_arrays.iteritems():
        micro_cmd = "{0:0{3}X}{1}{2:0{3}X}".format(start_char, length, command_byte, 2)
        uart_port = UART_PORTS[int(micro_num[-1])]
        command_array[uart_port] = []
        print micro_num, cid_array
        if len(cid_array) > 16:
            id_arrays = split_id_array(cid_array)
            for id_array in id_arrays:
                for id in id_array:
                    micro_cmd += '{0:0{1}X}'.format(int(id), 2)
        elif len(cid_array) <= 0:
            pass
        elif len(cid_array) == 1:
            micro_cmd += '{0:0{1}X}'.format(int(cid_array[0]), 2)
        else:
            for id in cid_array:
                micro_cmd += '{0:0{1}X}'.format(int(id), 2)

        micro_cmd += '{0}{1:0{2}X}'.format(checksum, stop_char, 2)
        length = calculate_length(micro_cmd)
        micro_cmd = micro_cmd[:2] + "{0:0{1}X}".format(length, 2) + micro_cmd[3:]
        checksum = calculate_checksum(micro_cmd)
        micro_cmd = micro_cmd[:len(micro_cmd) - 3] + "{0:0{1}X}".format(checksum, 2) + micro_cmd[len(micro_cmd) - 2:]
        command_array[uart_port].append(micro_cmd)

    print command_array

    return command_array, "ARRAY"


def translate_all_led(command):
    """
    Translate the command for all LEDs
    into the proper micro command
    @param command: incoming json command from DSP
    @return: String micro command
    """
    parameters = button_numbers['all']
    length = '0'
    checksum = '0'
    command_byte = command_dict['set_led_button']

    micro_cmd = "{0:0{6}X}{1}{2:0{6}X}{3:0{6}X}{4}{5:0{6}X}".format(start_char, length, command_byte,
                                                                         parameters, checksum, stop_char, 2)
    length = calculate_length(micro_cmd)
    micro_cmd = micro_cmd[:2] + "{0:0{1}X}".format(length, 2) + micro_cmd[3:]
    checksum = calculate_checksum(micro_cmd)
    micro_cmd = micro_cmd[:len(micro_cmd)-3] + "{0:0{1}X}".format(checksum, 2) + micro_cmd[len(micro_cmd)-2:]

    return micro_cmd, 'ALL'


def calculate_length(micro_cmd):
    return len(micro_cmd[4:len(micro_cmd)-4])


def calculate_checksum(micro_cmd):
    return bin(int(micro_cmd, 16))[2:].count("1")


def translate_single_led(command):
    """
    Translate the command for a single LED
    into the proper micro command
    @param command: incoming json command from DSP
    @return: String micro command
    """
    parameter = int(command['component_id'])
    uart_port = UART_PORTS[map_arrays['micro'][int(parameter)]]
    length = '0'
    checksum = '0'
    command_byte = command_dict['set_led_button']

    micro_cmd = "{0:0{6}X}{1}{2:0{6}X}{3:0{6}X}{4}{5:0{6}X}".format(start_char, length, command_byte,
                                                                    parameter, checksum, stop_char, 2)

    length = calculate_length(micro_cmd)
    micro_cmd = micro_cmd[:2] + "{0:0{1}X}".format(length, 2) + micro_cmd[3:]
    checksum = calculate_checksum(micro_cmd)
    micro_cmd = micro_cmd[:len(micro_cmd) - 3] + "{0:0{1}X}".format(checksum, 2) + micro_cmd[len(micro_cmd) - 2:]

    return micro_cmd, uart_port


if __name__ == "__main__":
    t = {"category": "BTN","component": "LED","component_id":
        ["34", "35", "123", "203","78","56","25","201","106"],
         "action": "SET", "value":"1"}
    button_command_array_handler(t)
    #translate_all_led("")

class MessageHandler:

    def __init__(self, json_request):
        self.json_request = json_request
        self.fw_version = FIRMWARE_VERSION
        self.category = self.json_request['category']
        self.component = self.json_request['component']
        self.component_id = self.json_request['component_id']
        self.action = self.json_request['action']
        self.value = self.json_request['value']

    def process_command(self):
        """
        Run the corresponding method based on the
        category from the incoming JSON
        @return: Response back to DSP
        """
        if self.category == "CFG":
            response, (uart_command, uart_port) = self.run_config_cmd()
        elif self.category == "STS":
            response, (uart_command, uart_port) = self.run_status_cmd()
        elif self.category == "BTN":
            response, (uart_command, uart_port) = self.run_button_cmd()
        elif self.category == "ENC":
            response, (uart_command, uart_port) = self.run_encoder_cmd()
        else:
            response, (uart_command, uart_port) = error_response(1)
        return response, (uart_command, uart_port)

    def run_config_cmd(self):
        """
        Run the set of config commands, which
        include firmware and status.
        @return: FW or status response
        """
        uart_port = UART_PORTS[0]
        micro_cmd = translate_cfg_cmd(self.json_request)
        response = self.json_request
        response['action'] = "="
        return response, (micro_cmd, uart_port)

    def run_encoder_cmd(self):
        """
        Run the set of encoder commands, which
        include changing the sensitivity as well
        as the position of the encoder
        @return: Encoder response to DSP
        """
        uart_port = UART_PORTS[0]
        micro_cmd = translate_enc_cmd(self.json_request)
        response = self.json_request
        response['action'] = "="
        return response, (micro_cmd, uart_port)

    def run_status_cmd(self):
        """
        Run the status command on the system.
        Runs status_utils check_status method which
        checks memory availability as well as other
        key system status reports
        @return: Status command response to DSP
        """
        response = self.json_request
        response['action'] = "="
        if self.json_request['component_id'] == "FW":
            response['value'] = self.fw_version
            return response, ("FW", None)
        elif self.json_request['component_id'] == "STS":
            response['value'] = status_utils.check_status()
            return response, ("STS", None)
        else:
            return error_response(1)

    def run_button_cmd(self):
        """
        Run command with a single LED, Switch or list
        of LEDs or Switches, or using ALL which
        results in all LEDs turning on. This command will
        split and allocate all incoming panel_ids into <16
        len arrays
        @return:
        """
        command = deepcopy(self.json_request)
        response = deepcopy(self.json_request)
        response['action'] = "="

        comp = command['component']
        cid = command['component_id']

        if comp == 'LED' and isinstance(cid, list):
            micro_command, uart_port = button_command_array_handler(command)
            return response, (micro_command, uart_port)
        elif comp == 'LED' and cid == 'ALL':
            micro_command, uart_port = translate_all_led(command)
            return response, (micro_command, uart_port)
        elif comp == 'LED':
            micro_command, uart_port = translate_single_led(command)
            return response, (micro_command, uart_port)
        else:
            return error_response(1)
