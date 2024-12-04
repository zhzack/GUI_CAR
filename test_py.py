import socket
import json
import random
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))

x = 0
y = 0

features = {
    "断连中": 0x0,
    "RKE": 0x1,
    "迎宾 W": 0x2,
    "车左": 0x4,
    "车右": 0x8,
    "车后": 0x10,
    "车内": 0x20
}
list = list(features.values())

for i in range(0, 10000000000):

    # 创建符合格式的数据
    data = {
        'path3': {'x': x, 'y': y}
    }

    ble=list[(int(i) % (len(list)))]
    # ble=list[2]

    data = f'car,{y},{x},1 UWB1,{x},{y},1 UWB2,{-x},{y},0 BLE,{x},{-y},0 '
    data = f'car1,{y},{x},1 UWB1,{x},{
        y},1 UWB2,{-x},{y},2 BLE,{ble},{-y},1 '
    # print(ble)
    # client_socket.send(json.dumps(data).encode('utf-8'))
    client_socket.send(data.encode('utf-8'))

    x += random.randint(-100, 100)
    y += random.randint(-100, 100)
    time.sleep(0.1)

# 关闭连接
client_socket.close()
