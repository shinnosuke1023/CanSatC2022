from threading import Thread

import flightpin
import motor
import web_server
import cansatNichrome
from time import sleep

mode = 0  # 0=気球搭載モード 1=落下中モード 2=パラシュート切り離しモード 3=走行モード


def web_server_boot():
    web_thread = Thread(target=web_server.web_server_loop)
    web_thread.daemon = True
    web_thread.start()


def auto_jettison():
    sleep(30)
    cansatNichrome.cutting()


def launching_mode():
    global mode
    flightpin.waiting()  # フライトピンが抜けるまでここでブロッキング
    # フライトピンの状態を確認
    mode += 1


def falling_mode():
    global mode
    web_server.cansat_status = "falling mode"
    web_server_boot()
    jettison_thread = Thread(target=auto_jettison)
    jettison_thread.daemon = True
    jettison_thread.start()
    mode += 1


def separating_mode():
    global mode
    # ニクロム線を加熱してテグスを切断する
    # cansatNichrome.cutting()
    mode += 1


def running_mode():
    global mode
    web_server.cansat_status = "running mode"
    motor.GPIO.output(motor.STBY, motor.GPIO.HIGH)
    # モーターを制御、角度を取得
    while True:
        try:
            if not web_server.deg_thread.is_alive():  # not忘れたら死ぬぞ!!!!!
                web_server.deg_reader_boot()
        except KeyboardInterrupt:
            end()
            exit()
        except Exception as e:
            print(e)


def end():
    motor.end()
    web_server.process.kill()
    exit()


def mainloop():
    launching_mode()
    falling_mode()
    separating_mode()
    running_mode()


if __name__ == "__main__":
    mainloop()
