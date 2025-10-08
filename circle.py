# -*- coding: utf-8 -*-

from djitellopy import Tello
import time
import traceback

def main():
    """
    Telloを操作して、カメラを円の中心に向けたまま、
    指定した角度（370度）だけ円を描いて飛行するメイン関数。
    """
    tello = Tello()

    try:
        print("Telloに接続します...", flush=True)
        tello.connect()
        print("接続完了。", flush=True)

        battery = tello.get_battery()
        print(f"バッテリー残量: {battery}%", flush=True)
        if battery < 20:
            print("バッテリー残量が20%未満です。飛行を中止します。", flush=True)
            return

        print("離陸します。", flush=True)
        tello.takeoff()
        time.sleep(2)

        # --- ここから円を描く飛行 ---
        # ★★★今回の修正点★★★
        # 右回転(yaw_speedがプラス)しながら左に移動(sideways_speedがマイナス)することで、
        # カメラが円の中心を向くようになります。
        sideways_speed = -25

        # 旋回速度（この値が大きいほど、円を描くのが速くなる）
        yaw_speed = 35

        print("現在の機体の向きを記録します...", flush=True)
        start_yaw = None
        while start_yaw is None:
            start_yaw = tello.get_yaw()
            time.sleep(0.1)
        print(f"開始角度: {start_yaw}度", flush=True)

        print("RC制御で、カメラを中心に向けたまま円を描きます...", flush=True)
        # 左右移動(第1引数)と旋回(第4引数)を同時に与えることで、
        # カメラを円の中心に向けたまま飛行します。
        tello.send_rc_control(sideways_speed, 0, 0, yaw_speed)

        # 飛行開始時刻と角度の記録
        loop_start_time = time.time()
        last_yaw = start_yaw
        total_rotation = 0.0

        # 累積回転角度が目標（370度）に達するまでループ
        target_rotation = 370

        while abs(total_rotation) < target_rotation:
            # タイムアウト処理: 25秒以上ループが続いたら強制的に抜ける
            if time.time() - loop_start_time > 25:
                print("タイムアウトしました。ループを強制終了します。", flush=True)
                break

            current_yaw = tello.get_yaw()
            if current_yaw is None:
                time.sleep(0.1)
                continue

            # 角度の変化量を計算（-180度〜180度のラップアラウンドを考慮）
            delta_yaw = current_yaw - last_yaw
            if delta_yaw > 180:
                delta_yaw -= 360
            elif delta_yaw < -180:
                delta_yaw += 360

            # 変化量を累積していく
            total_rotation += delta_yaw
            last_yaw = current_yaw

            time.sleep(0.1)

        print(f"目標の{target_rotation}度に近い回転を完了しました (実績: {int(total_rotation)}度)。", flush=True)


    except (Exception, KeyboardInterrupt):
        print("\nエラーまたは中断リクエストを検知しました。", flush=True)
        print(traceback.format_exc())

    finally:
        # ★★★ここからが必ず実行される、より安全になった終了処理★★★
        print("最終処理に入ります...", flush=True)

        try:
            if tello.is_flying:
                print("安全のため、まずホバリングさせます。", flush=True)
                tello.send_rc_control(0, 0, 0, 0)

                # RC制御からコマンドモードへの移行を確実にするため、1秒待機します。
                time.sleep(1)

                print("着陸します。", flush=True)
                tello.land()

            # Telloとの接続をクリーンに終了させます。
            print("接続を終了します。", flush=True)
            tello.end()

        except Exception as e:
            print(f"終了処理中にエラーが発生しました: {e}", flush=True)
            # どうしても終了できない場合の最後の手段
            tello.end()

        print("プログラム終了。", flush=True)


if __name__ == '__main__':
    main()

