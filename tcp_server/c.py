import socket
import time

# 目标广播地址和端口
BROADCAST_IP = "255.255.255.255"
PORT = 5005
MESSAGE = "DISCOVER_SERVER"

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # 允许广播

sock.settimeout(2)  # 设置超时时间，避免无限等待
sock.bind(("", 0))  # 绑定任意可用端口

print("正在发送广播消息...")
sock.sendto(MESSAGE.encode(), (BROADCAST_IP, PORT))  # 发送广播

try:
    data, server = sock.recvfrom(1024)  # 等待服务端回复
    response = data.decode()
    print(f"收到服务器响应: {response}")
    
    # 解析服务器地址
    _, server_ip, server_port = response.split(",")
    print(f"找到服务器: IP={server_ip}, PORT={server_port}")
except socket.timeout:
    print("未找到服务器，超时退出。")

sock.close()
