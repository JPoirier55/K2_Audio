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
    time.sleep(.1)
    ser.close()
      
def error_response(error_id):
    error_descs = ['Invalid category or component.', 
                   'State (parameter) out of range', 
                   'Command not understood/syntax invalid.']
    response = {}
    response['category'] = "ERROR"
    response['component'] = ""
    response['component_id'] = ""
    response['action'] = "="
    response['value'] = str(error_id)
    response['description'] = error_descs[error_id-1]
    return response
      
            
class MessageHandler:

    def __init__(self, json_request):
      self.json_request = json_request
      self.uart_ports = UART_PORTS
      self.fw_version = FIRMWARE_VERSION
      self.category = ''
      self.component = ''
      self.action = ''
      self.component_id = ''
      self.value = ''
      self.parse_command()
    
    def parse_command(self):
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
      uart_port = self.uart_ports[0]
      send_uart(self.json_request, uart_port)
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
    
    def translate_uart_port(self, panel_id):
      return self.uart_ports[map_arrays['micro'][panel_id]]
      
    def translate_logical_id(self, component_id):
      return map_arrays['logical'][component_id-1]      
    
    def run_button_cmd(self):
      response = deepcopy(self.json_request)
      response['action'] = "="
      if self.json_request['component'] == "LED": 
        if len(self.json_request['component_id']) == 1:
          try:
              int(self.json_request['component_id'])
          except Exception as e:
            return error_response(1)
          uart_port = self.translate_uart_port(int(self.json_request['component_id']))
          logical_id = self.translate_logical_id(self.json_request['component'])
          ##create method to handle sending correct msg to micro
          if not uart_port:
            return error_response(2)
          send_uart(self.json_request, uart_port)
        elif self.json_request['component_id'] == 'ALL':
          for uart_port in self.uart_ports:
            send_uart(self.json_request, uart_port)
        elif len(self.json_request['component_id']) > 1:
          led_array = self.json_request['component_id']
          for led in led_array:
            try:
              int(led)
            except Exception as e:
              return error_response(1)
          for led in led_array:
            request = self.json_request
            request['component_id'] = led
            uart_port = self.translate_uart_port(int(led))
            send_uart(request, uart_port)
        else:
          return error_response(1)
      else:
        return error_response(1)
      return response
      
    def run_encoder_cmd(self):
      uart_port = self.uart_ports[0]
      send_uart(self.json_request, uart_port)
      response = self.json_request
      response['action'] = "="  
      return response

