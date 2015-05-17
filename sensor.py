import RPi.GPIO as GPIO



class SensorController(object):
    def __init__(self):
        self.sensor1 = 17
        self.sensor2 = 22
        GPIO.setmode(GPIO.BCM)

    def AddSensor(self, port, callback, bounce):
        GPIO.setup(port, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(port, GPIO.FALLING, callback=callback, bouncetime=bounce)
