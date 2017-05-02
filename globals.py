"""
FILE:   globals.py
DESCRIPTION: All global variables contained in one module used by 
tcp_server.py

WRITTEN BY: Jake Poirier

MODIFICATION HISTORY:

date           programmer         modification
-----------------------------------------------
4/5/17          JDP                original
"""

import Adafruit_BBIO.GPIO as GPIO

GPIO.setup('P8_39', GPIO.OUT)
GPIO.setup('P8_41', GPIO.OUT)
GPIO.setup('P8_43', GPIO.OUT)
GPIO.setup('P8_45', GPIO.OUT)

GPIO.setup('P8_40', GPIO.IN)
GPIO.setup('P8_42', GPIO.IN)
GPIO.setup('P8_44', GPIO.IN)
GPIO.setup('P8_46', GPIO.IN)

GPIO.output("P8_39", GPIO.LOW)
GPIO.output("P8_41", GPIO.LOW)
GPIO.output("P8_43", GPIO.LOW)
GPIO.output("P8_45", GPIO.LOW)

RTS_GPIOS = ['/sys/class/gpio/gpio71/value', '/sys/class/gpio/gpio73/value',
             '/sys/class/gpio/gpio75/value', '/sys/class/gpio/gpio77/value']
GPIO_EDGE_FDS = ['/sys/class/gpio/gpio71/edge', '/sys/class/gpio/gpio73/edge',
                 '/sys/class/gpio/gpio75/edge', '/sys/class/gpio/gpio77/edge']

CTS_GPIOS = ['P8_45', 'P8_43', 'P8_41', 'P8_39']

DEBUG = True
DEV_UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2']
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
xUART_PORTS = ['/dev/ttyO1', '/dev/ttyO1', '/dev/ttyO1', '/dev/ttyO1']

MICRO_ACK = bytearray.fromhex('E8018069EE')
MICRO_ERR = bytearray.fromhex('E8018069EE')
BB_ACK = bytearray('E8018069EE')
DSP_SERVER_IP = '192.168.255.88'
DSP_SERVER_PORT = 65000
MICRO_STATUS = 'E80231001BEE'
ALL_LEDS = 'E80240F80123EE'
ALL_LEDS_OFF = 'E80240F80022EE'
SERIAL_TIMEOUT = 1
SERIAL_BAUDRATE = 115200
SOCKET_TIMEOUT = 1

FIRMWARE = {'1': '001',
            '2': '002',
            '3': '003',
            '4': '004',
            '5': '005',
            '6': '006',
            '7': '007'}

ERROR_DESCS = ['Invalid category or component.',
               'State (parameter) out of range',
               'Command not understood/syntax invalid.']

STATUS_TCP = {"category": "STS", "component": "SYS",
              "component_id": "STS", "action": "=", "value": "1"}

EXECUTE_LED_LIST = bytearray.fromhex('E802440000EE')
