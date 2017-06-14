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

# -------- Setup all GPIOs for RTS ----------
GPIO.setup('P8_39', GPIO.IN)
GPIO.setup('P8_41', GPIO.IN)
GPIO.setup('P8_43', GPIO.IN)
GPIO.setup('P8_45', GPIO.IN)

# -------- Setup all GPIOs for CTS ----------
GPIO.setup('P8_40', GPIO.OUT)
GPIO.setup('P8_42', GPIO.OUT)
GPIO.setup('P8_44', GPIO.OUT)
GPIO.setup('P8_46', GPIO.OUT)

# -------- Initially set CTS to low ---------
GPIO.output("P8_40", GPIO.LOW)
GPIO.output("P8_42", GPIO.LOW)
GPIO.output("P8_44", GPIO.LOW)
GPIO.output("P8_46", GPIO.LOW)

# -------- Setup events for RTS -------------
GPIO.add_event_detect("P8_39", GPIO.RISING)
GPIO.add_event_detect("P8_41", GPIO.RISING)
GPIO.add_event_detect("P8_43", GPIO.RISING)
GPIO.add_event_detect("P8_45", GPIO.RISING)

RTS_GPIOS = ['/sys/class/gpio/gpio70/value', '/sys/class/gpio/gpio72/value',
             '/sys/class/gpio/gpio74/value', '/sys/class/gpio/gpio76/value']
GPIO_EDGE_FDS = ['/sys/class/gpio/gpio70/edge', '/sys/class/gpio/gpio72/edge',
                 '/sys/class/gpio/gpio74/edge', '/sys/class/gpio/gpio76/edge']
CTS_GPIOS = ['P8_46', 'P8_44', 'P8_42', 'P8_40']

# DEBUG not true by default - run_configs.py changes this
DEBUG = False

# TCP client not connected by default - run_configs.py changes this
TCP_ON = False

UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']

# Set of static commands that will be sent from BB to micro
# that do not need any allocation methods to be built
MICRO_ACK = bytearray.fromhex('E8018069EE')
MICRO_ERR = bytearray.fromhex('E8018069EE')
MICRO_STATUS = bytearray.fromhex('E80231001BEE')
ALL_LEDS = bytearray.fromhex('E8034001F824EE')
ALL_LEDS_OFF = bytearray.fromhex('E8034000F823EE')
EXECUTE_LED_LIST = bytearray.fromhex('E80244000000EE')
SINGLE_TEST_LED = bytearray.fromhex('E8034001012DEE')
SINGLE_TEST_LED_OFF = bytearray.fromhex('E8034001002CEE')

# Debug values for DSP server - configuration contains
# real server IP and port under run_configs.py
DSP_SERVER_IP = '127.0.0.1'
DSP_SERVER_PORT = 65000

# Serial and socket globals
SERIAL_BAUDRATE = 115200
SOCKET_TIMEOUT = 1
SERIAL_TIMEOUT = 1

# Static messages for both err and status
ERROR_DESCS = ['Invalid category or component.',
               'State (parameter) out of range',
               'Command not understood/syntax invalid.']

STATUS_TCP = {"category": "STS", "component": "SYS",
              "component_id": "STS", "action": "=", "value": "1"}
