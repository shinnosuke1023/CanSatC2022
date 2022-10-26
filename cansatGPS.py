import serial
from micropyGPS import MicropyGPS

my_gps = MicropyGPS(9, 'dd')

"""旧コード
s = serial.Serial('/dev/serial0', 9600, timeout=10)


def get_gps():
    for x in s.readline().decode('utf-8'):
        my_gps.update(x)
    return my_gps.latitude[0], my_gps.longitude[0]
"""


def run_gps():
    """GPSモジュールを読み、GPSオブジェクトを更新する"""

    s = serial.Serial('/dev/serial0', 9600, timeout=10)

    s.readline()  # 最初の1行捨てる
    while True:
        sentence = s.readline().decode("utf-8")

        if sentence[0] != '$':
            continue

        for x in sentence:
            my_gps.update(x)


