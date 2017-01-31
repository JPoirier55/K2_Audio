import serial
import json


class SerialSendHandler:
    """
      Class to handle all outgoing serial 
      messages to controllers
      
      args: baudrate-default 115200
            timeout-default None (allows no waiting on sending)
    """
    def __init__(self, baudrate=115200, timeout=None):
        self.baudrate = baudrate
        self.timeout = timeout

    def test_connection(self):
        if self.port.is_open():
            return True

    def send_uart(self, json_command, uart_send):
        print 'sending: ', json.dumps(json_command), uart_send, " ", self.baudrate

        ser = serial.Serial(uart_send, baudrate=self.baudrate, timeout=self.timeout)
        ser.write(json.dumps(json_command) + '\n')
        ser.close()


class CommandHandler:
    """
      Class to setup what the outgoing
      uart command will look like
      
      args: command - incoming json string with null at end
      
    """
    def __init__(self, command):
        self.uarts = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
        # Slice off null character from end
        self.json_command = json.loads(command[0:-1])
        self.serial_handler = SerialSendHandler()

    def calculate_controller(self, seat_id):
        """
          Calculate controller and seat ids for
          outgoing message
          
          ex. seat 150 will fall into controller 3, so
          uart ttyO4 will handle that data.
        """
        controller_id = seat_id % 4
        if seat_id < 51:
            uart_send = self.uarts[0]
        elif seat_id >= 51 and seat_id < 102:
            uart_send = self.uarts[1]
        elif seat_id >= 102 and seat_id < 153:
            uart_send = self.uarts[2]
        else:
            uart_send = self.uarts[3]

        return uart_send, controller_id

    def create_state(self, state):
        """
          Function to calculate state based on 
          incoming state number. 
          
          ****Functionality tentative to protocol defined by K2****
        """
        state_json = {'green': 0,
                      'red': 0,
                      'fast': 0,
                      'slow': 0,
                      'alt': 0}
        if state == 0:
          return state_json
        elif state == 1:
          state_json['green'] = 1
          state_json['slow'] = 1
          return state_json
        elif state == 2:
          state_json['red'] = 1
          state_json['slow'] = 1
        elif state == 3:
          state_json['green'] = 1
          state_json['fast'] = 1
        else:
          return state_json

    def build_uart_command(self, seat_id, controller_id, state):
        """
          Build json of outgoing data to controller
          
          ex. Seat 150 will calculate to 150%51 = 48,
          so from the function above, controller id = 3, 
          and seat id = 48. Json object will look like:
          
          {"controller_id": 3,
           "seat_id": 48,
           "state": {"green": 0...},
           }
        """
        controller_seat = seat_id % 51
        json = {'controller_id': controller_id,
                'seat_id': controller_seat,
                'state': state}
        return json

    def process_command(self):
        """
          Access point for accumulating all functionality
          for sending data out
        """
        print self.json_command
        seat_id = self.json_command['seat_id']
        state = self.create_state(self.json_command['state'])
        uart_send, controller_id = self.calculate_controller(seat_id)
        json_command = self.build_uart_command(seat_id, controller_id, state)
        self.serial_handler.send_uart(json_command, uart_send)
