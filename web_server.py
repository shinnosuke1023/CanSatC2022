from flask import Flask, Response, render_template, request
from threading import Thread
import cansatGPS, cansatGyro, motor
import cansatNichrome
import subprocess
from time import sleep
import urllib


# 画質設定
QUALITY = 10
WIDTH = 240
HEIGHT = 135
FPS = 15


app = Flask(__name__)
process = None
deg_thread = None
cansat_status = "launching mode"
image_num = 0


def gps_reader_boot():
    gps_thread = Thread(target=cansatGPS.run_gps, args=())
    gps_thread.daemon = True
    gps_thread.start()


def deg_reader_boot():
    global deg_thread
    deg_thread = Thread(target=cansatGyro.get_deg, args=())
    deg_thread.daemon = True
    deg_thread.start()


def camera_server_boot(width, height, fps, quality):
    global process
    process = subprocess.Popen("exec mjpg_streamer -o './output_http.so -w ./www -p 8081' -i './input_raspicam.so "
                               "-x {0} -y {1} -fps {2} -q {3}'".format(width, height, fps, quality),
                               cwd=r"/home/cansat/mjpg-streamer/mjpg-streamer-experimental", shell=True)


@app.route('/status_feed')
def status_feed():
    def generate():
        yield cansat_status

    return Response(generate(), mimetype='text')


@app.route('/data_feed')
def data_feed():
    def generate():
        x_deg = cansatGyro.cansat_pitch
        y_deg = cansatGyro.cansat_roll
        latitude = cansatGPS.my_gps.latitude[0]
        longitude = cansatGPS.my_gps.longitude[0]
        yield "ピッチ角:" + str(round(x_deg, 2)) + "° ロール角:" + str(round(y_deg, 2)) + "°\n"\
              "N:" + str(round(latitude, 7)) + "°, E:" + str(round(longitude, 7)) + "°"

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


@app.route("/small_down", methods=["POST"])
def small_down():
    key = request.form["keyDown"]
    timeout = float(request.form["timeout"])
    key = key.lower()
    print(key)
    print(timeout)
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
    sleep(timeout)
    motor.func_brake()
    print("ブレーキ")
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


@app.route("/change_resolution", methods=["POST"])
def change_resolution():
    global process, WIDTH, HEIGHT
    resolution = request.form["resolution"]
    print(resolution)
    process.kill()
    width, height = resolution.split("x")
    print(width, height)
    WIDTH = int(width)
    HEIGHT = int(height)
    print(WIDTH, HEIGHT)
    camera_server_boot(WIDTH, HEIGHT, FPS, QUALITY)
    return ""


@app.route("/change_fps", methods=["POST"])
def change_fps():
    global process, FPS
    fps = request.form["fps"]
    print(fps)
    process.kill()
    FPS = int(fps)
    camera_server_boot(WIDTH, HEIGHT, FPS, QUALITY)
    return ""


@app.route("/change_duty_rate", methods=["POST"])
def change_duty_rate():
    rate = request.form["dutyRate"]
    print(rate)
    motor.val = int(rate)
    motor.p_a.ChangeDutyCycle(motor.val)
    motor.p_b.ChangeDutyCycle(motor.val)
    return ""


@app.route("/save_image", methods=["POST"])
def save_image():
    global image_num
    latitude = cansatGPS.my_gps.latitude[0]
    longitude = cansatGPS.my_gps.longitude[0]
    path = f"./static/{image_num}_N{round(latitude, 7)}_E{round(longitude, 7)}"
    try:
        with urllib.request.urlopen("http://127.0.0.1:8081/?action=snapshot") as web_file:
            image = web_file.read()
            with open(path, "wb") as local_image:
                local_image.write(image)
    except urllib.error.URLError as e:
        print(e)
    image_num += 1


@app.route("/")
def index():
    return render_template("index.html", currentResolution=f"{WIDTH}x{HEIGHT}", currentFPS=f"{FPS}fps")


@app.route("/shutdown", methods=["GET"])
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


def web_server_loop():
    gps_reader_boot()
    deg_reader_boot()
    camera_server_boot(WIDTH, HEIGHT, FPS, QUALITY)
    app.run(host="0.0.0.0", threaded=True, port=8080)
    process.kill()


if __name__ == "__main__":
    web_server_loop()
