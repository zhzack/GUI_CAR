import socket

# 监听端口
PORT = 5005
BROADCAST_IP = "255.255.255.255"

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # 允许广播
sock.bind(("", PORT))  # 监听所有IP的广播

print("服务器正在监听广播请求...")

while True:
    data, addr = sock.recvfrom(1024)  # 接收广播数据
    print(f"收到来自 {addr} 的广播消息: {data.decode()}")

    if data.decode() == "DISCOVER_SERVER":  # 如果是客户端的探测请求
        response = f"SERVER_HERE,{socket.gethostbyname(socket.gethostname())},{PORT}"
        sock.sendto(response.encode(), addr)  # 回复客户端
        print(f"已回复 {addr} : {response}")
