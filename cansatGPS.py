from re import T
import serial
from micropyGPS import MicropyGPS

my_gps = MicropyGPS(9, 'dd')
s = serial.Serial('/dev/serial0', 9600, timeout=10)


def get_gps():
    for x in s.readline().decode('utf-8'):
        my_gps.update(x)
    return my_gps.latitude[0], my_gps.longitude[0]


