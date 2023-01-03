# CanSat 2022 C班 プログラム
## main.py
* 他のプログラムを呼び出す。エラーハンドリングもここ<br>
* SSHでこれを実行する

## web_sever.py
* 実質メインプログラム<br>
* Flaskを用いてユーザーに操作画面を提供する

## cansatGPS.py
* micropyGPS.pyを呼び出す
* while で変数書き換えるやっつけ実装

## micropyGPS.py
* シリアル通信でGPSデータを取得する
* どっかから拾ってきたやつ

## cansatGyro.py
* MPU6050から加速度、角速度を取得して大雑把な角度を出力するプログラム
* while で変数書き換えるやっつけ実装

## cansatNichrome.py
* sleepでFET起動するお手軽仕様

## flightpin.py
* フライトピン抜けるまでblockingするだけのお手軽仕様

## motor.py
* モータドライバー、モーターの制御
* 外から関数実行して動かす

## 総括
* class使えればよかったなぁ