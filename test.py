from djitellopy import Tello

# Telloオブジェクトを作成
tello = Tello()

# Telloに接続
tello.connect()




# 離陸
tello.takeoff()

# 着陸
tello.land()
