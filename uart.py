import serial
import json


class SerialSendHandler:
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
    def __init__(self, command):
        self.uarts = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
        self.json_command = json.loads(command)
        self.serial_handler = SerialSendHandler()

    def calculate_controller(self, seat_id):
        # modid = seat_id%4
        #uart_send = self.uarts[0]
        if seat_id < 51:
            uart_send = self.uarts[0]
        elif seat_id >= 51 and seat_id < 102:
            uart_send = self.uarts[1]
        elif seat_id >= 102 and seat_id < 153:
            uart_send = self.uarts[2]
        else:
            uart_send = self.uarts[3]
        #uart_send = self.uarts[str(modid)]
        return uart_send

    def build_uart_command(self, seat_id, state):
        controller_seat = seat_id % 51
        controller_id = seat_id % 4
        if state == 0:
          green = 0
          red = 0
        json = {'controller_id': controller_id,
                'seat_id': controller_seat,
                'state': state}
        return json

    def process_command(self):
        print self.json_command
        seat_id = self.json_command['seat_id']
        state = self.json_command['state']
        uart_send = self.calculate_controller(seat_id)
        json_command = self.build_uart_command(seat_id, state)
        self.serial_handler.send_uart(json_command, uart_send)
