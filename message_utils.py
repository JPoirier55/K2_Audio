"""
FILE:   message_utils.py
DESCRIPTION: Set of utility functions used for handling
and processing the messages that come from the DSP and require
manipulation before sending to micros.

WRITTEN BY: Jake Poirier

"""
from button_led_map import *
from command_map import *

DEBUG = True
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']


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


def allocate_micro_cmds(json_command):
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
        'micro_1': [6,7,90],
        'micro_2': [8],
        'micro_3': []}
    """
    micro_commands = {'micro_0': [],
                      'micro_1': [],
                      'micro_2': [],
                      'micro_3': []}

    cid_array = json_command['component_id']
    for cid in cid_array:
        try:
            if int(cid) < len(map_arrays['micro']):
                micro_num = map_arrays['micro'][(int(cid))-1]
                micro_commands['micro_' + str(micro_num)].append(translate_logical_id(cid))
        except:
            continue
    return micro_commands


def calculate_length(micro_cmd):
    """
    Calculates length of micro commmand
    by look at size after length, up to 
    checksum
    
    @param micro_cmd: 
    @return: length of command 
    """
    return len(micro_cmd[2:len(micro_cmd)-2])


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
        sum += micro_cmd[i]
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
    micro_cmd[1] = length
    checksum = calculate_checksum_bytes(micro_cmd)
    micro_cmd[-2] = checksum
    return micro_cmd


def translate_led_array(json_command):
    """
    Takes incoming json_command with an array of BTN IDs
    and splits them into messages that contain a maximum
    of 16 len BTN ids, and put them to the corresponding
    micro based on the logical ids for each id.
    
    @param json_command: DSP cmd with array of panel_ids
    @return: Dict with uart ports and strings for micro
    commands
    """
    command_array = {}
    logical_ids = []
    command_byte = command_dict['set_led_list']

    for id in json_command['component_id']:
        try:
            if int(id) < len(map_arrays['micro']):
                logical_ids.append(translate_logical_id(id))
        except:
            continue

    cid_arrays = allocate_micro_cmds(json_command)

    for micro_num, cid_array in cid_arrays.iteritems():
        if len(cid_array) > 0:
            micro_cmd = bytearray([start_char, 0, command_byte])
            uart_port = UART_PORTS[int(micro_num[-1])]
            command_array[uart_port] = []

            # Handle an array that ends up being longer than 16 for one micro
            if len(cid_array) > 16:
                id_arrays = split_id_array(cid_array)

                for id_array in id_arrays:
                    for id in id_array:
                        micro_cmd.append(int(id))
                    for i in range(16 - len(id_array)):
                        micro_cmd.append(0)
                    micro_cmd.append(0)
                    micro_cmd.append(stop_char)
                    micro_cmd = finalize_cmd(micro_cmd)
                    command_array[uart_port].append(micro_cmd)

                    micro_cmd = bytearray([start_char, 0, command_byte])

            # Handle array that is less than 16 for one micro
            else:
                for id in cid_array:
                    micro_cmd.append(int(id))
                for i in range(16 - len(cid_array)):
                    micro_cmd.append(0)
                micro_cmd.append(0)
                micro_cmd.append(stop_char)
                micro_cmd = finalize_cmd(micro_cmd)
                command_array[uart_port].append(micro_cmd)

    return command_array, "ARRAY"


def translate_all_led():
    """
    Translate the command for all LEDs
    into the proper micro command
    
    @param command: incoming json command from DSP
    @return: String micro command
    """
    parameters = button_numbers['all']
    command_byte = command_dict['set_led_button']

    micro_cmd = bytearray([start_char, 0, command_byte, parameters, 0, stop_char])

    micro_cmd = finalize_cmd(micro_cmd)

    return micro_cmd, 'ALL'


def translate_cfg_cmd(json_command):
    """
    Translated incoming DSP json command to a
    more condensed version to be sent to the micro
    as a possible set of bytes/ascii chars. Will be
    updated for new protocol between bb and micros
    
    @param json_command: DSP json command
    @return: new micro command
    """
    # TODO: add in pwm duty cycle and period for mikes protocol
    comp = json_command['component']
    cid = json_command['component_id']
    action = json_command['action']
    value = json_command['value']
    parameters = int(hex(int(value))[2:], 16)

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
    elif comp == 'PWM' and cid == 'CYC' and action == 'SET':
        command_byte = command_dict['set_led_pwm_dcyc']
    elif comp == 'PWM' and cid == 'PER' and action == 'SET':
        command_byte = command_dict['set_led_pwm_period']
    else:
        return None, None

    if action == 'GET':
        micro_cmd = bytearray([start_char, 0, command_byte, 0, stop_char])
    else:
        micro_cmd = bytearray([start_char, 0, command_byte, parameters, 0, stop_char])
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
    action = command['action']
    try:
        value = int(command['value'])
        parameters = int(hex(int(value))[2:], 16)
        if value > 100:
            return None, None
    except:
        return None, None

    if comp == 'DIS' and action == 'SET':
        command_byte = command_dict['set_enc_disp']
    elif comp == 'DIS' and action == 'GET':
        command_byte = command_dict['get_enc_disp']
    elif comp == 'POS' and action == 'SET':
        command_byte = command_dict['set_enc_pos']
    elif comp == 'POS' and action == 'GET':
        command_byte = command_dict['get_enc_pos']
    else:
        return None, None

    if action == 'GET':
        micro_cmd = bytearray([start_char, 0, command_byte, 0, stop_char])
    else:
        micro_cmd = bytearray([start_char, 0, command_byte, parameters, 0, stop_char])

    micro_cmd = finalize_cmd(micro_cmd)
    return micro_cmd, UART_PORTS[0]


def translate_single_led(json_command):
    """
    Translate the command for a single LED
    into the proper micro command
    
    @param command: incoming json command from DSP
    @return: String micro command
    """
    try:
        parameter = int(json_command['component_id'])
        value = int(json_command['value'])
    except:
        return None, None
    if parameter > len(map_arrays['micro']):
        return None, None

    uart_port = UART_PORTS[map_arrays['micro'][parameter-1]]

    if json_command['action'] == 'GET':
        command_byte = command_dict['get_led_button']
        micro_cmd = bytearray([start_char, 0, command_byte, parameter,
                               0, stop_char])
    else:
        command_byte = command_dict['set_led_button']
        micro_cmd = bytearray([start_char, 0, command_byte, value, parameter,
                               0, stop_char])

    micro_cmd = finalize_cmd(micro_cmd)
    return micro_cmd, uart_port


def check_fw_or_status(json_command):
    """
    Method to build micro command
    to check both firmware and status
    of the micros.
    
    @param request: 
    @return: micro command, uart ports
    """
    if json_command['component_id'] == 'FW':
        command_byte = command_dict['get_fw_version']
        micro_cmd = bytearray([start_char, 0, command_byte, 0, stop_char])
    else:
        command_byte = command_dict['get_panel_status']
        micro_cmd = bytearray([start_char, 0, command_byte, 0, stop_char])

    micro_cmd = finalize_cmd(micro_cmd)
    return micro_cmd, 'ALL'


class MessageHandler:
    """
    Class to handle allocation of certain commands in category
     
    Categories:
    Configuration
    LED/Switch
    Encoder
    Status
    """
    def __init__(self):
        pass

    def parse_json(self, json_request):
        """
        Splits up tcp dsp json into class variables
        
        @param json_request: incoming dsp JSON 
        @return: None
        """
        self.json_request = json_request
        self.category = self.json_request['category']
        self.component = self.json_request['component']
        self.component_id = self.json_request['component_id']
        self.action = self.json_request['action']
        self.value = self.json_request['value']

    def run_config_cmd(self):
        """
        Run the set of config commands, which
        include firmware and status.
        
        @return: FW or status response
        """
        micro_command, uart_port = translate_cfg_cmd(self.json_request)
        return micro_command, uart_port

    def run_encoder_cmd(self):
        """
        Run the set of encoder commands, which
        include changing the sensitivity as well
        as the position of the encoder
        
        @return: Encoder response to DSP
        """
        micro_command, uart_port = translate_enc_cmd(self.json_request)
        return micro_command, uart_port

    def run_status_cmd(self):
        """
        Run the status command on the system.
        Runs status_utils check_status method which
        checks memory availability as well as other
        key system status reports
        
        @return: Status command response to DSP
        """
        if self.json_request['component_id'] == "FW" or self.json_request['component_id'] == "STS":
            micro_command, uart_port = check_fw_or_status(self.json_request)
            return micro_command, uart_port
        else:
            return None, None

    def run_button_cmd(self):
        """
        Run command with a single LED, Switch or list
        of LEDs or Switches, or using ALL which
        results in all LEDs turning on. This command will
        split and allocate all incoming panel_ids into <16
        len arrays
        
        @return: tuple of format: micro command, uart port

        """
        try:
            value = int(self.json_request['value'])
            if value > 7:
                return None, None
        except:
            return None, None

        if self.component == 'LED' and isinstance(self.component_id, list):
            micro_command, uart_port = translate_led_array(self.json_request)
            return micro_command, uart_port
        elif self.component == 'LED' and self.component_id == 'ALL':
            micro_command, uart_port = translate_all_led()
            return micro_command, uart_port
        elif self.component == 'LED':
            micro_command, uart_port = translate_single_led(self.json_request)
            return micro_command, uart_port
        else:
            return None, None
