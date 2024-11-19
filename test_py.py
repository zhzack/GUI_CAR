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
    client_socket.send(json.dumps(data).encode('utf-8'))
    x+= random.randint(-1, 1)
    y+= random.randint(-1, 1)
    time.sleep(0.001)

# 关闭连接
client_socket.close()
