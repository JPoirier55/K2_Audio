
import Adafruit_BBIO.GPIO as GPIO
import time
GPIO.setup('P8_45', GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup('P8_45', GPIO.IN)

# GPIO.setup('P8_45', GPIO.OUT)
low = False
while True:
    print 'test'
    # if low:
    #     low = False
    #     GPIO.output('P8_45', GPIO.LOW)
    # else:
    #     low = True
    #     GPIO.output('P8_45', GPIO.HIGH)
    time.sleep(1)
