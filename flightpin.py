import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN)


def waiting():
    while GPIO.input(16) == GPIO.HIGH:
        time.sleep(0.5)
        print("フライトピンはささったままよ！")

    else:
        print("フライトピン抜けたよ！")


if __name__ == "__main__":
    waiting()