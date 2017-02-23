import Adafruit_BBIO.GPIO as GPIO
import time
#GPIO.setup('P8_8', GPIO.OUT)
GPIO.setup('P8_8', GPIO.IN)

# GPIO.add_event_detect("P8_8")
#
# if GPIO.event_detected("P8_8"):
#     print 'event detected'


#GPIO.output("P8_8", GPIO.LOW)
# time.sleep(1)
# GPIO.output("P8_8", GPIO.HIGH)
# time.sleep(1)
# GPIO.output("P8_8", GPIO.LOW)
# time.sleep(1)

while True:
    if GPIO.input("P8_8"):
        print 'high'
    else:
        print 'low'
    time.sleep(.5)