import cv2
from flask import Flask, Response, render_template, request
import random
from time import time, sleep
import cansatGPS, cansatGyro, motor
import cansatNichrome

import cansatGyro

QUALITY = 5
encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), QUALITY]

# Webカメラの設定情報
DEVICE_ID = 0

WIDTH = 320
HEIGHT = 180
FPS = 30

app = Flask(__name__)

# VideoCapture オブジェクトを取得します
capture = cv2.VideoCapture(DEVICE_ID)
# カメラの解像度・FPSの変更
capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
capture.set(cv2.CAP_PROP_FPS, FPS)


def get_frames():
    while True:
        ret, frame = capture.read()
        image = frame
        ret, jpg_str = cv2.imencode(".jpeg", image, encode_param)
        yield b"--boundary\r\nContent-Type:image/jpeg\r\n\r\n" + jpg_str.tobytes() + b"\r\n\r\n"


@app.route("/video_feed")
def video_feed():
    return Response(get_frames(), mimetype="multipart/x-mixed-replace; boundary=boundary")


@app.route('/status_feed')
def status_feed():
    def generate():
        yield "test"

    return Response(generate(), mimetype='text')


@app.route('/deg_feed')
def deg_feed():
    def generate():
        gen = cansatGyro.get_deg()
        x_sum = 0
        y_sum = 0
        deg_len = 10
        for i in range(10):
            x, y = gen.__next__()
            x_sum += x
            y_sum += y
        x_deg = x_sum / deg_len
        y_deg = y_sum / deg_len
        # x_deg = random.randrange(0, 90)
        # y_deg = random.randrange(0, 90)
        yield "ピッチ角:" + str(round(x_deg, 2)) + "° ロール角:" + str(round(y_deg, 2)) + "°"

    return Response(generate(), mimetype='text')


@app.route('/gps_feed')
def gps_feed():
    def generate():
        latitude, longitude = cansatGPS.get_gps()
        # latitude, longitude = (random.randrange(0, 90), random.randrange(0, 90))
        yield "北緯:" + str(latitude) + "°, 北緯:" + str(longitude) + "°"

    return Response(generate(), mimetype='text')


@app.route("/keyboard_down", methods=["POST"])
def keyboard_down():
    key = request.form["keyDown"]
    key = key.lower()
    print(key)
    if key == "w":
        motor.forward()
        print("前進")
    if key == "s":
        motor.reverse()
        print("後進")
    if key == "d":
        motor.right()
        print("右旋回")
    if key == "a":
        motor.left()
        print("左旋回")
    return ""


@app.route("/keyboard_up", methods=["POST"])
def keyboard_up():
    key = request.form["keyUp"]
    key = key.lower()
    print(key)
    motor.func_brake()
    print("ブレーキ")
    return ""


@app.route("/jettison", methods=["POST"])
def jettison():
    cansatNichrome.cutting()
    print("パラシュート分離")
    return ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/shutdown", methods=["GET"])
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


def web_server_loop():
    app.run(host="0.0.0.0", threaded=True, port=8080)
    capture.release()


if __name__ == "__main__":
    web_server_loop()
