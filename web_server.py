import cv2
from flask import Flask, Response, render_template, request

QUALITY = 5
encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), QUALITY]

# Webカメラの設定情報
DEVICE_ID = 0

WIDTH = 480
HEIGHT = 270
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
        # image = cv2.resize(frame, (480, 270))
        image = frame
        ret, jpg_str = cv2.imencode(".jpeg", image, encode_param)
        yield b"--boundary\r\nContent-Type:image/jpeg\r\n\r\n" + jpg_str.tobytes() + b"\r\n\r\n"


@app.route("/video_feed")
def video_feed():
    return Response(get_frames(), mimetype="multipart/x-mixed-replace; boundary=boundary")


@app.route("/keyboard_down", methods=["POST"])
def keyboard_down():
    key = request.form["keyDown"]
    key = key.lower()
    print(key)
    return ""


@app.route("/keyboard_up", methods=["POST"])
def keyboard_up():
    key = request.form["keyUp"]
    key = key.lower()
    print(key)
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
