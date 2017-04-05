

import Adafruit_BBIO.GPIO as GPIO

GPIO.setup('P8_41', GPIO.IN)
GPIO.setup('P8_42', GPIO.IN)
GPIO.setup('P8_43', GPIO.IN)
GPIO.setup('P8_44', GPIO.IN)

GPIO.setup('P8_7', GPIO.OUT)
GPIO.setup('P8_8', GPIO.OUT)
GPIO.setup('P8_9', GPIO.OUT)
GPIO.setup('P8_10', GPIO.OUT)

GPIO.setup('USR0', GPIO.OUT)
GPIO.setup('USR1', GPIO.OUT)
GPIO.setup('USR2', GPIO.OUT)
GPIO.setup('USR3', GPIO.OUT)

RTS_GPIOS = ['/sys/class/gpio/gpio74/value', '/sys/class/gpio/gpio75/value',
             '/sys/class/gpio/gpio72/value', '/sys/class/gpio/gpio73/value']
GPIO_EDGE_FDS = ['/sys/class/gpio/gpio74/edge', '/sys/class/gpio/gpio75/edge',
                 '/sys/class/gpio/gpio72/edge', '/sys/class/gpio/gpio73/edge']
CTS_GPIOS = ['/sys/class/gpio/gpio66/value', '/sys/class/gpio/gpio67/value',
             '/sys/class/gpio/gpio68/value', '/sys/class/gpio/gpio69/value']

DEBUG = True
DEV_UART_PORTS = ['/dev/ttyO1', '/dev/ttyO2']
xUART_PORTS = ['/dev/ttyO1', '/dev/ttyO2', '/dev/ttyO4', '/dev/ttyO5']
UART_PORTS = ['/dev/ttyO1', '/dev/ttyO1','/dev/ttyO1','/dev/ttyO1']

MICRO_ACK = bytearray.fromhex('E8018069EE')
MICRO_ERR = bytearray.fromhex('E8018069EE')
BB_ACK = bytearray('E8018069EE')
DSP_SERVER_IP = '192.168.255.88'
DSP_SERVER_PORT = 65000
MICRO_STATUS = 'E80231001BEE'
ALL_LEDS = 'E80240F80123EE'
ALL_LEDS_OFF = 'E80240F80022EE'

