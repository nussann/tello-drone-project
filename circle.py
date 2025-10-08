# -*- coding: utf-8 -*-

from djitellopy import Tello
import time
import traceback
import threading
import cv2 # OpenCVライブラリ

# --- ここから録画用の設定 ---

# 録画を続けるかどうかを管理するフラグ
keep_recording = True

def video_recorder(tello: Tello):
    """
    別スレッドで実行されるビデオ録画用の関数。
    """
    # Telloのビデオストリームからフレームを読み取る準備
    frame_reader = tello.get_frame_read()

    # 現在の日時で動画ファイル名を生成
    video_filename = f"tello_video_{time.strftime('%Y-%m-%d_%H-%M-%S')}.avi"

    # 動画を保存するための設定 (AVI形式, 25 FPS, 960x720)
    # Telloのカメラは 960x720 の解像度
    video = cv2.VideoWriter(video_filename,
                            cv2.VideoWriter_fourcc(*'XVID'),
                            25, (960, 720))

    print(f"録画を開始しました。ファイル名: {video_filename}", flush=True)

    while keep_recording:
        # Telloから最新のフレーム（映像の1コマ）を取得
        frame = frame_reader.frame
        # そのフレームを動画ファイルに書き込む
        video.write(frame)
        # 非常に短い待機時間を入れる
        time.sleep(1 / 30) # 30 FPS程度になるように調整

    # 録画を終了する
    video.release()
    print("録画を停止し、ファイルを保存しました。", flush=True)

# --- ここまで録画用の設定 ---


def main():
    """
    Telloを操作して、カメラを円の中心に向けたまま円を描き、その様子を録画する。
    """
    tello = Tello()
    recorder_thread = None
    global keep_recording

    try:
        print("Telloに接続します...", flush=True)
        tello.connect()
        print("接続完了。", flush=True)

        battery = tello.get_battery()
        print(f"バッテリー残量: {battery}%", flush=True)
        if battery < 20:
            print("バッテリー残量が20%未満です。飛行を中止します。", flush=True)
            return

        # --- 録画の開始 ---
        keep_recording = True
        tello.streamon()
        recorder_thread = threading.Thread(target=video_recorder, args=(tello,))
        recorder_thread.start()
        time.sleep(2) # 録画スレッドが安定するまで少し待つ

        print("離陸します。", flush=True)
        tello.takeoff()
        time.sleep(2)

        # --- 円を大きくするための変更 ---
        # 左右の移動速度を-25から-30にすることで、円の半径が約20%大きくなる
        sideways_speed = -30
        yaw_speed = 35

        print("現在の機体の向きを記録します...", flush=True)
        start_yaw = None
        while start_yaw is None:
            start_yaw = tello.get_yaw()
            time.sleep(0.1)
        print(f"開始角度: {start_yaw}度", flush=True)

        print("RC制御で、カメラを中心に向けたまま円を描きます...", flush=True)
        tello.send_rc_control(sideways_speed, 0, 0, yaw_speed)

        loop_start_time = time.time()
        last_yaw = start_yaw
        total_rotation = 0.0
        target_rotation = 370

        while abs(total_rotation) < target_rotation:
            if time.time() - loop_start_time > 25:
                print("タイムアウトしました。ループを強制終了します。", flush=True)
                break

            current_yaw = tello.get_yaw()
            if current_yaw is None:
                time.sleep(0.1)
                continue

            delta_yaw = current_yaw - last_yaw
            if delta_yaw > 180: delta_yaw -= 360
            elif delta_yaw < -180: delta_yaw += 360

            total_rotation += delta_yaw
            last_yaw = current_yaw
            time.sleep(0.1)

        print(f"目標の{target_rotation}度に近い回転を完了しました (実績: {int(total_rotation)}度)。", flush=True)

    except (Exception, KeyboardInterrupt):
        print("\nエラーまたは中断リクエストを検知しました。", flush=True)
        print(traceback.format_exc())

    finally:
        print("最終処理に入ります...", flush=True)

        try:
            if tello.is_flying:
                print("安全のため、まずホバリングさせます。", flush=True)
                tello.send_rc_control(0, 0, 0, 0)
                time.sleep(1)
                print("着陸します。", flush=True)
                tello.land()

            # --- 録画の停止処理 ---
            if keep_recording:
                keep_recording = False
            if recorder_thread is not None:
                recorder_thread.join() # 録画スレッドが完全に終わるのを待つ

            tello.streamoff()
            print("接続を終了します。", flush=True)
            tello.end()

        except Exception as e:
            print(f"終了処理中にエラーが発生しました: {e}", flush=True)
            tello.end()

        print("プログラム終了。", flush=True)

if __name__ == '__main__':
    main()

