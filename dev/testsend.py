import serial
import json


class UART:
	uart1 = '/dev/ttyO1'
	uart2 = '/dev/ttyO2'
	uart4 = '/dev/ttyO4'
	uart5 = '/dev/ttyO5'
	uart0 = '/dev/ttyO0'
	

def send_dsp_command(command):
	
	c = json.loads(command)
	seat_id = c['seat_id']

	uart_num = seat_id % 60
	print 'id:',  c['seat_id']
	print uart_num
	
	print 'within dsp command: ' + command

	#ser = serial.Serial('/dev/ttyO0', 9600)

	#ser.write(command)

	#ser.close()
