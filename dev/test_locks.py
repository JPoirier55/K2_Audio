import serial
from threading import Lock
import threading
import time
import select
import Adafruit_BBIO.GPIO as GPIO

GPIO.setup('P8_7', GPIO.IN)
GPIO.setup('P8_8', GPIO.IN)
GPIO.setup('P8_9', GPIO.OUT)
GPIO.setup('P8_10', GPIO.OUT)

GPIO.setup('USR0', GPIO.OUT)
GPIO.output('USR0', GPIO.HIGH)


s = serial.Serial('/dev/ttyO4', 115200)
s2 = serial.Serial('/dev/ttyO4', 115200)

lock1 = Lock()

def m_1():

    while True:
        print '1: trying to acquire'
        if lock1.acquire():
            print '1: lock aquired'
            try:
                ser = serial.Serial('/dev/ttyO4', 115200)
                print '1: sending'
                ser.write('1: hello there')
                time.sleep(3)
            finally:
                lock1.release()
                print '1: lock released'
        time.sleep(1)

def m_2():

    while True:
        print '2: trying to acquire'
        if lock1.acquire():
            print '2: lock aquired'
            try:
                ser = serial.Serial('/dev/ttyO4', 115200)
                print '2: sending'
                ser.write('2: hello there')
                time.sleep(3)
            finally:
                lock1.release()
                print '2: lock released'
        time.sleep(1)

def s():
    print 'starting'
    print 'opening'


    print 'writing edge'


    print 'reading value'

    while True:
        # if GPIO.input("P8_7"):
        #     print 'on'
        # else:
        #     print 'off'
        # gpio = GPIO.input("P8_7")


        gpio = open('/sys/class/gpio/gpio67/value', 'r+')
        gpio2 = open('/sys/class/gpio/gpio66/value', 'r+')

        gpio_edge = open('/sys/class/gpio/gpio67/edge', 'w')
        gpio_edge.write("both")
        gpio_edge2 = open('/sys/class/gpio/gpio66/edge', 'w')
        gpio_edge2.write("both")
        val = gpio.read()
        val2 = gpio2.read()
        s = [gpio, gpio2]


        r, w, e = select.select([], [], s, 5)
        # if e:
        #     print val
        for g in e:
            print 'sdfsd'
            if g == gpio:
                print val
            elif g == gpio2:
                print val2
        # for readable in r:
        #     if readable == gpio:
        #         print gpio.read()




# if __name__ == '__main__':
    # s()
    # t1 = threading.Thread(target=m_1)
    # t2 = threading.Thread(target=m_2)
    # t1.start()
    # t2.start()

