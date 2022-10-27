# -*- coding: utf-8 -*-

import smbus
import math
from time import sleep, time

DEV_ADDR = 0x68

ACCEL_XOUT = 0x3b
ACCEL_YOUT = 0x3d
ACCEL_ZOUT = 0x3f
TEMP_OUT = 0x41
GYRO_XOUT = 0x43
GYRO_YOUT = 0x45
GYRO_ZOUT = 0x47

PWR_MGMT_1 = 0x6b
PWR_MGMT_2 = 0x6c

bus = smbus.SMBus(1)
bus.write_byte_data(DEV_ADDR, PWR_MGMT_1, 0)

cansat_roll = 0
cansat_pitch = 0


def read_word(adr):
    high = bus.read_byte_data(DEV_ADDR, adr)
    low = bus.read_byte_data(DEV_ADDR, adr + 1)
    val = (high << 8) + low
    return val


# Sensor data read
def read_word_sensor(adr):
    val = read_word(adr)
    if (val >= 0x8000):  # minus
        return -((65535 - val) + 1)
    else:  # plus
        return val


def get_temp():
    temp = read_word_sensor(TEMP_OUT)
    x = temp / 340 + 36.53  # data sheet(register map)記載の計算式.
    return x


def getGyro():
    x = read_word_sensor(GYRO_XOUT) / 131.0
    y = read_word_sensor(GYRO_YOUT) / 131.0
    z = read_word_sensor(GYRO_ZOUT) / 131.0
    return [x, y, z]


def getAccel():
    x = read_word_sensor(ACCEL_XOUT) / 16384.0
    y = read_word_sensor(ACCEL_YOUT) / 16384.0
    z = read_word_sensor(ACCEL_ZOUT) / 16384.0
    return [x, y, z]


def get_deg():
    global cansat_roll, cansat_pitch
    gyro_roll = 0
    gyro_pitch = 0
    cansat_roll = 0
    cansat_pitch = 0
    pregx = 0
    pregy = 0
    while 1:
        ax, ay, az = getAccel()
        gx, gy, gz = getGyro()

        # print ('{:4.3f},{:4.3f}, {:4.3f}, {:4.3f},{:4.3f}, {:4.3f},' .format(gx, gy, gz, ax, ay, az))
        if az == 0:
            continue
        roll = math.atan(ay / az) * 57.324
        pitch = math.atan(-ax / math.sqrt(ay * ay + az * az)) * 57.324

        # print ('{:4.3f},{:4.3f}, {:4.3f}, {:4.3f},{:4.3f}, {:4.3f},' .format(gx, gy, gz, ax, ay, az))
        if az == 0:
            continue
        roll = math.atan(ay / az) * 57.324
        pitch = math.atan(-ax / math.sqrt(ay * ay + az * az)) * 57.324

        gyro_roll = cansat_roll + (pregx + gx) * 0.1 / 2
        gyro_pitch = cansat_pitch + (pregy + gy) * 0.1 / 2
        cansat_roll = gyro_roll * 0.5 + roll * 0.5
        cansat_pitch = gyro_pitch * 0.5 + pitch * 0.5
        # print('{:4.3f}, {:4.3f}, {:4.3f}, {:4.3f}, {:4.3f}, {:4.3f}, {:4.3f}'.format(az, pitch, roll, gyro_pitch, gyro_roll, cansat_pitch, cansat_roll))
        pregx = gx
        pregy = gy
        # yield cansat_pitch, cansat_roll
        sleep(0.1)
