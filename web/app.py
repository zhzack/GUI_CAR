from flask import Flask, render_template, jsonify, request
import socket
import threading

app = Flask(__name__)

# 共享变量
current_angle = 0
current_distance = 0

# TCP 服务器配置
TCP_HOST = '0.0.0.0'  # 监听所有 IP
TCP_PORT = 5005       # 监听端口


def set_data(a, b):
    current_angle = a
    current_distance = b


def handle_client(client_socket, addr):
    """处理单个 TCP 客户端的长连接"""
    global current_angle, current_distance
    print(f"Connected to {addr}")

    try:
        while True:
            data = client_socket.recv(1024).decode().strip()  # 接收数据
            if not data:
                print(f"Client {addr} disconnected")
                break  # 客户端断开连接

            print(f"Received from {addr}: {data}")
            try:
                angle, distance = map(float, data.split(','))  # 解析 "45,120"
                if 0 <= angle <= 360:
                    set_data(angle,distance)
                    # current_angle = angle
                    # current_distance = distance
                    client_socket.sendall(b"Data received\n")
                else:
                    client_socket.sendall(b"Invalid angle\n")
            except ValueError:
                client_socket.sendall(b"Invalid format\n")
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        client_socket.close()


def tcp_server():
    """TCP 服务器，支持多个长连接客户端"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(5)
    print(f"TCP Server listening on {TCP_HOST}:{TCP_PORT}")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(
            client_socket, addr), daemon=True).start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_angle', methods=['GET'])
def get_angle():
    """获取当前角度和距离"""
    return jsonify({'angle': current_angle, 'distance': current_distance})


@app.route('/set_angle', methods=['POST'])
def set_angle():
    """手动设置角度"""
    global current_angle
    data = request.get_json()
    angle = data.get('angle')
    if angle is not None and 0 <= angle <= 360:
        current_angle = angle
        return jsonify({'message': 'Angle updated successfully', 'angle': current_angle}), 200
    else:
        return jsonify({'error': 'Invalid angle. Please set an angle between 0 and 360.'}), 400


if __name__ == '__main__':
    # 启动 TCP 服务器线程
    threading.Thread(target=tcp_server, daemon=True).start()

    # 启动 Flask 服务器
    app.run(debug=True, host="0.0.0.0", port=5000)
