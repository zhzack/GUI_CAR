import socket
import json
import random
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))

x = 0
y = 0

for i in range(0,10000000000):

    # 创建符合格式的数据
    data = {
        'path3': {'x': x, 'y': y}
    }
    
    data=f'car,{y},{x},1 UWB1,{x},{y},1 UWB2,{-x},{y},0 BLE,{x},{-y},0 '
    data=f'car1,{y},{x},1 UWB11,{x},{y},0 UWB2,{-x},{y},0 BLE,{x},{-y},0 '
    # client_socket.send(json.dumps(data).encode('utf-8'))
    client_socket.send(data.encode('utf-8'))

    x+= random.randint(-10, 10)
    y+= random.randint(-10, 10)
    time.sleep(0.1)

# 关闭连接
client_socket.close()
