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

GPIO.setup('P8_39', GPIO.IN)
GPIO.setup('P8_41', GPIO.IN)
GPIO.setup('P8_43', GPIO.IN)
GPIO.setup('P8_45', GPIO.IN)

GPIO.setup('P8_40', GPIO.OUT)
GPIO.setup('P8_42', GPIO.OUT)
GPIO.setup('P8_44', GPIO.OUT)
GPIO.setup('P8_46', GPIO.OUT)

GPIO.output("P8_40", GPIO.LOW)
GPIO.output("P8_42", GPIO.LOW)
GPIO.output("P8_44", GPIO.LOW)
GPIO.output("P8_46", GPIO.LOW)

GPIO.add_event_detect("P8_39", GPIO.RISING)
GPIO.add_event_detect("P8_41", GPIO.RISING)
GPIO.add_event_detect("P8_43", GPIO.RISING)
GPIO.add_event_detect("P8_45", GPIO.RISING)


RTS_GPIOS = ['/sys/class/gpio/gpio70/value', '/sys/class/gpio/gpio72/value',
             '/sys/class/gpio/gpio74/value', '/sys/class/gpio/gpio76/value']
GPIO_EDGE_FDS = ['/sys/class/gpio/gpio70/edge', '/sys/class/gpio/gpio72/edge',
                 '/sys/class/gpio/gpio74/edge', '/sys/class/gpio/gpio76/edge']

CTS_GPIOS = ['P8_46', 'P8_44', 'P8_42', 'P8_40']

DEBUG = True
TCP_ON = False

DEV_UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2']
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
xUART_PORTS = ['/dev/ttyO1', '/dev/ttyO1', '/dev/ttyO1', '/dev/ttyO1']

MICRO_ACK = bytearray.fromhex('E8018069EE')
MICRO_ERR = bytearray.fromhex('E8018069EE')
BB_ACK = bytearray('E8018069EE')
DSP_SERVER_IP = '192.168.255.88'
DSP_SERVER_PORT = 65000
MICRO_STATUS = bytearray.fromhex('E80231001BEE')
ALL_LEDS = bytearray.fromhex('E80240F80123EE')
ALL_LEDS_OFF = bytearray.fromhex('E80240F80022EE')
SERIAL_TIMEOUT = 1
SERIAL_BAUDRATE = 115200
SOCKET_TIMEOUT = 1

ERROR_DESCS = ['Invalid category or component.',
               'State (parameter) out of range',
               'Command not understood/syntax invalid.']

STATUS_TCP = {"category": "STS", "component": "SYS",
              "component_id": "STS", "action": "=", "value": "1"}

EXECUTE_LED_LIST = bytearray.fromhex('E802440000EE')
