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
import select
import json
from copy import deepcopy
import subprocess
import sys
import time
import status_utils
from button_led_map import map_arrays

FIRMWARE_VERSION = "001"
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']


def send_uart(json_command, uart_port):
    """
    Simple uart sending method, possibly deprecated
    in the near future for something more robust
    @param json_command: Incoming json command to be sent
    @param uart_port: Port to send data to
    @return: None
    """
    # print 'sending: ', json.dumps(json_command), uart_port
    ser = serial.Serial('/dev/ttyO4', baudrate=115200, timeout=None)
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
    
    return response


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


def translate_cfg_cmd(command):
    """
    Translated incoming DSP json command to a
    more condensed version to be sent to the micro
    as a possible set of bytes/ascii chars. Will be
    updated for new protocol between bb and micros
    @param command: DSP json command
    @return: new micro command
    """
    comp = command['component']
    cid = command['component_id']
    micro_cmd = {'value': command['value']}
      
    if comp == 'RTE' and cid == 'SLO':
        micro_cmd['category'] = 'S_RATE'
    elif comp == 'RTE' and cid == 'FST':
        micro_cmd['category'] = 'F_RATE'
    elif comp == 'CYC' and cid == 'SLO':
        micro_cmd['category'] = 'S_DCYC'
    elif comp == 'CYC' and cid == 'FST':
        micro_cmd['category'] = 'F_DCYC'
    else:
        micro_cmd['category'] = 'E_SENS'
      
    return micro_cmd


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
    micro_cmd = {'value': command['value']}
    
    if comp == 'DIS':
      micro_cmd['category'] = 'E_DISP'
    else:
      micro_cmd['category'] = 'E_POSI'
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


def button_command_array_handler(command):
    """
    Takes incoming command with an array of BTN IDs
    and splits them into messages that contain a maximum
    of 16 len BTN ids, and put them to the corresponding
    micro based on the logical ids for each id.
    @param command: DSP cmd with array of panel_ids
    @return: Dict with set of messages

    """
    command_array = {}
    logical_ids = []
    
    for id in command['component_id']:
        logical_ids.append(translate_logical_id(id))
    
    cid_arrays = allocate_micro_cmds(command)
    for micro_num, cid_array in cid_arrays.iteritems():
        uart_port = UART_PORTS[int(micro_num[-1])]
        command_array[uart_port] = []
        micro_command = {'category': 'BN_LED',
                         'id': cid_array,
                         'value': command['value']}
        if len(cid_array) > 16:
            id_arrays = split_id_array(micro_command['id'])
            for id_array in id_arrays:
                micro_command['id'] = id_array
                command_array[uart_port].append((deepcopy(micro_command)))
        elif len(cid_array) <= 0:
            pass
        elif len(cid_array) == 1:
            micro_command['id'] = micro_command['id'][0]
            command_array[uart_port].append(micro_command)
        else:
            command_array[uart_port].append(micro_command)
    return command_array

        
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
            response = self.run_config_cmd()
        elif self.category == "STS":
            response = self.run_status_cmd()
        elif self.category == "BTN":
            response = self.run_button_cmd()
        elif self.category == "ENC":
            response = self.run_encoder_cmd()
        else:
            response = error_response(1)
        return response
      
    def run_config_cmd(self):
        # TODO: should be some type of try except, for when there is an error sending the cmd to micro
        """
        Run the set of config commands, which
        include firmware and status.
        @return: FW or status response
        """
        uart_port = UART_PORTS[0]
        micro_cmd = translate_cfg_cmd(self.json_request)
        send_uart(micro_cmd, uart_port)
        response = self.json_request
        response['action'] = "="
        return response
     
    def run_encoder_cmd(self):
        """
        Run the set of encoder commands, which
        include changing the sensitivity as well
        as the position of the encoder
        @return: Encoder response to DSP
        """
        # TODO: should be some type of try except, for when there is an error sending the cmd to micro

        uart_port = UART_PORTS[0]
        micro_cmd = translate_enc_cmd(self.json_request)
        send_uart(micro_cmd, uart_port)
        response = self.json_request
        response['action'] = "="
        return response

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
            return response
        elif self.json_request['component_id'] == "STS":
            response['value'] = status_utils.check_status()
            return response
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
        micro_command = ""
        command_array = []

        comp = command['component']
        cid = command['component_id']
        val = command['value']
      
        if comp == 'LED' and isinstance(cid, list):
            command_array = button_command_array_handler(command)
            for uart_port in command_array:
                for micro_command in command_array[uart_port]:
                    send_uart(micro_command, uart_port)
        elif comp == 'LED' and cid == 'ALL':
            micro_command = {'category': 'BN_LED',
                             'id': cid,
                             'value': val}
            for uart_port in UART_PORTS:
                send_uart(micro_command, uart_port)
        elif comp == 'LED':
            micro_command = {'category': 'BN_LED',
                             'id': cid,
                             'value': val}
            send_uart(micro_command, '')
        return response
