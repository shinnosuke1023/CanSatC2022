import time
import RPi.GPIO as GPIO


def cutting():
    GPIO.setmode(GPIO.BCM)
    channel = 26
    GPIO.setup(channel, GPIO.OUT)

    GPIO.output(channel, GPIO.HIGH)
    time.sleep(10)
    GPIO.output(channel, GPIO.LOW)

    GPIO.cleanup(channel)


if __name__ == "__main__":
    cutting()