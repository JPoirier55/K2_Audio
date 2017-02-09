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
    print 'sending: ', json.dumps(json_command), uart_port
    ser = serial.Serial(uart_port, baudrate=115200, timeout=None)
    ser.write(json.dumps(json_command) + '\n')
    time.sleep(.01)
    ser.close()
      
def error_response(error_id):
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
  return UART_PORTS[map_arrays['micro'][panel_id]]
  
def translate_logical_id(component_id):
  return map_arrays['logical'][(int(component_id))-1]

def translate_cfg_cmd(command):
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
      micro_cmd['category'] = 'ENC_SEN'
      
    return micro_cmd
    
def translate_enc_cmd(command):
    comp = command['component']
    micro_cmd = {'value': command['value']}
    
    if comp == 'DIS':
      micro_cmd['category'] = 'ENC_DIS'
    else:
      micro_cmd['category'] = 'ENC_POS'
    return micro_cmd
      
def split_id_array(id_array):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(id_array), 16):
        yield id_array[i:i + 16]
        
def allocate_micro_cmds(command):
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
    command_array = {}
    logical_ids = []
    
    for id in command['component_id']:
      logical_ids.append(translate_logical_id(id))
    
    cid_arrays = allocate_micro_cmds(command)
    for micro_num,cid_array in cid_arrays.iteritems():
      uart_port = UART_PORTS[int(micro_num[-1])]
      command_array[uart_port] = []
      micro_command = {'category': 'BTN_LED',
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
      if self.category == "CFG":
        response = self.run_config_cmd()
      elif self.category == "SYS":
        response = self.run_status_cmd()
      elif self.category == "BTN":
        response = self.run_button_cmd()
      elif self.category == "ENC":
        response = self.run_encoder_cmd()
      else:
        response = self.error_response(1)
      return response
      
    def run_config_cmd(self):
      uart_port = UART_PORTS[0]
      micro_cmd = translate_cfg_cmd(self.json_request)
      send_uart(micro_cmd, uart_port)
      response = self.json_request
      response['action'] = "="  
      return response 
     
    def run_encoder_cmd(self):
      uart_port = UART_PORTS[0]
      micro_cmd = translate_enc_cmd(self.json_request)
      send_uart(micro_cmd, uart_port)
      response = self.json_request
      response['action'] = "="  
      return response   
      
    def run_status_cmd(self):
      response = self.json_request
      response['action'] = "="
      if self.json_request['component_id'] == "FW":
        response['value'] = self.fw_version
        return response
      elif self.json_request['component_id'] == "STS":
        response['value'] =  status_utils.check_status()
        return response
      else:
        return error_response(1)      
    
    def run_button_cmd(self):
      command = deepcopy(self.json_request)
      response = deepcopy(self.json_request)
      response['action'] = "="
      
      command_array = {}
      
      comp = command['component']
      cid = command['component_id']
      val = command['value']
      
      if comp == 'LED' and isinstance(cid, list):          
        command_array = button_command_array_handler(command)
        for uart_port in command_array:
          for micro_command in command_array[uart_port]:
            send_uart(micro_command, uart_port)
      elif comp == 'LED' and cid == 'ALL':
        micro_command = {'category': 'BTN_LED',
                         'id': cid,
                         'value': val}
        for uart_port in self.uart_ports:
            send_uart(micro_command, uart_port)
      elif comp == 'LED' and isinstance(cid, int):
        micro_command = {'category': 'BTN_LED',
                         'id': cid,
                         'value': val}
      return response
    