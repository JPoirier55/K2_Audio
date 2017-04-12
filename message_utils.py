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
from copy import deepcopy
import status_utils
from button_led_map import *
from command_map import *

DEBUG = True
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
ERROR_DESCS = ['Invalid category or component.',
               'State (parameter) out of range',
               'Command not understood/syntax invalid.']


def error_response(error_id):
    """
    Error handler and builder
    @param error_id: ID of error
    @return: Error response in JSON format
    """
    response = {'category': 'ERROR',
                'component': '',
                'component_id': '',
                'action': '=',
                'value': str(error_id),
                'description': ERROR_DESCS[error_id-1]}

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


def calculate_length(micro_cmd):
    """
    Calculates length of micro commmand
    by look at size after length, up to 
    checksum
    @param micro_cmd: 
    @return: length of command 
    """
    return len(micro_cmd[4:len(micro_cmd)-2])/2


def calculate_checksum_string(micro_cmd):
    """
    Calculates checksum of an outgoing
    micro command that is currently of
    type string, uses only lease significant
    byte for command
    @param micro_cmd: 
    @return: checksum
    """
    sum = 0
    ba = bytearray.fromhex(str(micro_cmd[:-3]))
    for i in range(len(ba)):
        sum += ba[i]
    return sum % 0x100


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
    for i in range(len(micro_cmd)-2):
        sum += ord(micro_cmd[i])
    return sum % 0x100


def finalize_cmd(micro_cmd):
    """
    Takes command that is outgoing to 
    micro and injects both checksum and
    length in the final command to be 
    sent out
    @param micro_cmd: 
    @return: final micro command 
    """
    length = calculate_length(micro_cmd)
    micro_cmd = micro_cmd[:2] + "{0:0{1}X}".format(length, 2) + micro_cmd[3:]
    checksum = calculate_checksum_string(micro_cmd)
    micro_cmd = micro_cmd[:len(micro_cmd) - 3] + "{0:0{1}X}".format(checksum, 2) + micro_cmd[len(micro_cmd) - 2:]
    return micro_cmd


def translate_led_array(command):
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
    value = int(command['value'])
    command_byte = command_dict['set_led_list']
    length = '0'
    checksum = '0'

    for id in command['component_id']:
        logical_ids.append(translate_logical_id(id))

    cid_arrays = allocate_micro_cmds(command)

    for micro_num, cid_array in cid_arrays.iteritems():
        micro_cmd = "{0:0{4}X}{1}{2:0{4}X}{3:0{4}X}".format(start_char, length, command_byte, value, 2)
        uart_port = UART_PORTS[int(micro_num[-1])]

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
        micro_cmd = finalize_cmd(micro_cmd)
        command_array[uart_port] = (micro_cmd)

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
    micro_cmd = finalize_cmd(micro_cmd)

    return micro_cmd, 'ALL'


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
    length = '0'
    checksum = '0'
    parameters = value

    if comp == 'RTE' and cid == 'SLO' and action == 'SET':
        command_byte = command_dict['set_led_slow_rate']
    elif comp == 'RTE' and cid == 'SLO' and action == 'GET':
        command_byte = command_dict['get_led_slow_rate']
    elif comp == 'RTE' and cid == 'FST' and action == 'SET':
        command_byte = command_dict['set_led_fast_rate']
    elif comp == 'RTE' and cid == 'FST' and action == 'GET':
        command_byte = command_dict['get_led_fast_rate']
    elif comp == 'CYC' and cid == 'SLO' and action == 'SET':
        command_byte = command_dict['set_led_slow_dcyc']
    elif comp == 'CYC' and cid == 'SLO' and action == 'GET':
        command_byte = command_dict['get_led_slow_dcyc']
    elif comp == 'CYC' and cid == 'FST' and action == 'SET':
        command_byte = command_dict['set_led_fast_dcyc']
    elif comp == 'CYC' and cid == 'FST' and action == 'GET':
        command_byte = command_dict['get_led_fast_dcyc']
    elif comp == 'ENC' and cid == 'SEN' and action == 'SET':
        command_byte = command_dict['set_enc_sens']
    elif comp == 'ENC' and cid == 'SEN' and action == 'GET':
        command_byte = command_dict['get_enc_sens']
    else:
        return None
    if action == 'GET':
        micro_cmd = "{0:0{5}X}{1}{2:0{5}X}00{3}{4:0{5}X}".format(start_char, length, command_byte,
                                                                 checksum, stop_char, 2)
    else:
        micro_cmd = "{0:0{6}X}{1}{2:0{6}X}{3:0>2}{4}{5:0{6}X}".format(start_char, length, command_byte,
                                                                      parameters, checksum, stop_char, 2)
    micro_cmd = finalize_cmd(micro_cmd)

    return micro_cmd, UART_PORTS[0]


def translate_enc_cmd(command):
    """
    Translated incoming DSP json command to a
    more condensed version to be sent to the micro
    as a possible set of bytes/ascii chars. 
    @param command: DSP json command
    @return: new micro command
    """
    comp = command['component']
    value = command['value']
    action = command['action']
    length = '0'
    checksum = '0'
    parameters = value

    if comp == 'DIS' and action == 'SET':
        command_byte = command_dict['set_enc_disp']
    elif comp == 'DIS' and action == 'GET':
        command_byte = command_dict['get_enc_disp']
    elif comp == 'POS' and action == 'SET':
        command_byte = command_dict['set_enc_pos']
    elif comp == 'POS' and action == 'GET':
        command_byte = command_dict['get_enc_pos']
    else:
        return None
    if action == 'GET':
        micro_cmd = "{0:0{5}X}{1:0>2}{2:0{5}X}00{3:0>2}{4:0{5}X}".format(start_char, length, command_byte,
                                                                         checksum, stop_char, 2)
    else:
        micro_cmd = "{0:0{6}X}{1:0>2}{2:0{6}X}{3:0>2}{4:0>2}{5:0{6}X}".format(start_char, length, command_byte,
                                                                              parameters, checksum, stop_char, 2)

    micro_cmd = finalize_cmd(micro_cmd)
    return micro_cmd, UART_PORTS[0]


def translate_single_led(command):
    """
    Translate the command for a single LED
    into the proper micro command
    @param command: incoming json command from DSP
    @return: String micro command
    """
    parameter = int(command['component_id'])
    value = int(command['value'])
    uart_port = UART_PORTS[map_arrays['micro'][int(parameter)]]
    length = '0'
    checksum = '0'
    command_byte = command_dict['set_led_button']

    micro_cmd = "{0:0{7}X}{1}{2:0{7}X}{3:0{7}X}{4:0{7}X}{5}{6:0{7}X}".format(start_char, length, command_byte,
                                                                             value, parameter, checksum, stop_char, 2)

    micro_cmd = finalize_cmd(micro_cmd)

    return micro_cmd, uart_port


def handle_unsolicited(micro_command, uart_port):
    """
    Handles incoming unsolicited commands
    from the micro. First checks checksum
    then builds a tcp command to be sent
    to DSP
    @param micro_command: 
    @return: TCP command for dsp 
    """
    for b in micro_command:
        print ord(b)

    cmd = ord(micro_command[2])
    checksum = ord(micro_command[-2])
    print hex(checksum)

    cs = calculate_checksum_bytes(micro_command)
    print hex(cs)
    tcp_command = {}
    if checksum == cs:
        if cmd == 0x10:
            micro_button_number = ord(micro_command[3])
            if DEBUG:
                print ":".join("{:02x}".format(ord(c)) for c in micro_command)

            button_index = micro_array[uart_port]['logical'].index(micro_button_number)
            panel_button_number = micro_array[uart_port]['panel'][button_index]

            value = ord(micro_command[4])
            tcp_command = {'category': 'BTN',
                           'component': 'SW',
                           'component_id': panel_button_number,
                           'action': '=',
                           'value': value}

        elif cmd == 0x11:
            value = ord(micro_command[3])
            tcp_command = {'category': 'ENC',
                           'component': 'POS',
                           'component_id': '0',
                           'action': '=',
                           'value': value}

        elif cmd == 0xF0:
            value = ord(micro_command[3])
            tcp_command = {'category': 'ERROR',
                           'component': '',
                           'component_id': '',
                           'action': '=',
                           'value': value,
                           'description': ERROR_DESCS[value]}

        elif cmd == 0x90:
            value = ord(micro_command[3])
            tcp_command = {'category': 'EXCEPTION',
                           'component': '',
                           'component_id': '',
                           'action': '=',
                           'value': value}

        elif cmd == 0x80:
            tcp_command = {'category': 'ACK',
                           'component': '',
                           'component_id': '',
                           'action': '=',
                           'value': ''}

    return tcp_command


def check_fw_or_status(request):
    """
    Method to build micro command
    to check both firmware and status
    of the micros.
    @param request: 
    @return: micro command, uart ports
    """
    length = '0'
    checksum = '0'
    micro_cmd = ''

    if request == 'firmware':
        command_byte = command_dict['get_fw_version']
        micro_cmd = "{0:0{5}X}{1}{2:0{5}X}00{3}{4:0{5}X}".format(start_char, length, command_byte,
                                                                 checksum, stop_char, 2)

    if request == 'status':
        command_byte = command_dict['get_panel_status']
        micro_cmd = "{0:0{5}X}{1}{2:0{5}X}00{3}{4:0{5}X}".format(start_char, length, command_byte,
                                                                 checksum, stop_char, 2)

    finalize_cmd(micro_cmd)
    return micro_cmd, 'ALL'


class MessageHandler:

    def __init__(self, json_request):
        self.json_request = json_request
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
        micro_command, uart_port = translate_cfg_cmd(self.json_request)
        response = self.json_request
        response['action'] = "="
        return response, (micro_command, uart_port)

    def run_encoder_cmd(self):
        """
        Run the set of encoder commands, which
        include changing the sensitivity as well
        as the position of the encoder
        @return: Encoder response to DSP
        """
        micro_command, uart_port = translate_enc_cmd(self.json_request)
        response = self.json_request
        response['action'] = "="
        return response, (micro_command, uart_port)

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
            micro_command, uart_port = check_fw_or_status('firmware')
            response['action'] = '='
            return response, (micro_command, uart_port)

        elif self.json_request['component_id'] == "STS":
            micro_command, uart_port = check_fw_or_status('status')
            response['action'] = '='
            return response, (micro_command, uart_port)

        else:
            return error_response(1)

    def run_button_cmd(self):
        """
        Run command with a single LED, Switch or list
        of LEDs or Switches, or using ALL which
        results in all LEDs turning on. This command will
        split and allocate all incoming panel_ids into <16
        len arrays
        @return: tuple of format:
                    tcp_response, (micro command, uart port)

        """
        command = deepcopy(self.json_request)
        response = deepcopy(self.json_request)
        response['action'] = "="

        comp = command['component']
        cid = command['component_id']

        if comp == 'LED' and isinstance(cid, list):
            micro_command, uart_port = translate_led_array(command)
            return response, (micro_command, uart_port)
        elif comp == 'LED' and cid == 'ALL':
            micro_command, uart_port = translate_all_led(command)
            return response, (micro_command, uart_port)
        elif comp == 'LED':
            micro_command, uart_port = translate_single_led(command)
            return response, (micro_command, uart_port)
        else:
            return error_response(1)
