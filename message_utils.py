import serial
import select
import json
from copy import deepcopy
import time

FIRMWARE_VERSION = "001"
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']


def send_uart(json_command, uart_port):
    print 'sending: ', json.dumps(json_command), uart_port
    ser = serial.Serial(uart_port, baudrate=115200, timeout=None)
    ser.write(json.dumps(json_command) + '\n')
    time.sleep(.1)
    ser.close()

def check_status():
    """
      Need to set some status protocols for bbb with response codes
      check uarts
      check power
      check system functionality
      need restart?
      
    """
    board = True
    if board:
      return 1
    elif not board:
      return 2
    else:
      return 0
      
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
        status_value = check_status()
        response['value'] = status_value
        return response
      else:
        return error_response(1)
    
    def calculate_uart_port(self, seat_id):
      if seat_id > 0 and seat_id <= 23:
        return self.uart_ports[0]
      elif seat_id > 23 and seat_id <= 83:
        return self.uart_ports[1]
      elif seat_id > 83 and seat_id <= 143:
        return self.uart_ports[2]
      elif seat_id > 143 and seat_id <= 203:
        return self.uart_ports[3]
      else:
        return None       
    
    def run_button_cmd(self):
      response = deepcopy(self.json_request)
      response['action'] = "="
      if self.json_request['component'] == "LED": 
        if len(self.json_request['component_id']) == 1:
          try:
              int(self.json_request['component_id'])
          except Exception as e:
            return error_response(1)
          uart_port = self.calculate_uart_port(int(self.json_request['component_id']))
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
            uart_port = self.calculate_uart_port(int(led))
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

