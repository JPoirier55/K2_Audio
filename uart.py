import serial
import json

uart1 = '/dev/ttyO1'
uart2 = '/dev/ttyO2'
uart4 = '/dev/ttyO4'
uart5 = '/dev/ttyO5'
uart0 = '/dev/ttyO0'
baud_rate = 9600


def process_command(command):
    if len(command) > 1:
        for json_c in json.loads(command):
            seat_id = json_c['seat_id']
            state = json_c['state']

            uart_send = calculate_controller(seat_id)
            json_command = build_uart_command(seat_id, state)
            send_uart(json_command, uart_send)
    else:
        json_c = json.loads(command)
        seat_id = json_c['seat_id']
        state = json_c['state']

        uart_send = calculate_controller(seat_id)
        json_command = build_uart_command(seat_id, state)
        send_uart(json_command, uart_send)

def calculate_controller(seat_id):
    if seat_id < 60:
        uart_send = uart1
    if seat_id > 60:
        uart_send = uart4
    return uart_send

def build_uart_command(seat_id, state):
    uart_seat = seat_id % 60
    json = {'seat_id': uart_seat,
            'state': state}
    return json


def send_uart(json_command, uart_send):
    print 'sending: ', uart_send, " ", baud_rate
    ser = serial.Serial(uart_send, baud_rate)
    ser.write(json.dumps(json_command))
    ser.close()
