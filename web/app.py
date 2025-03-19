import logging
from flask import Flask, render_template, jsonify
import socket
import threading
import asyncio
import websockets
import json
from threading import Lock
import psutil

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 杀死占用端口的进程


def kill_process_by_port(port):
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port:
            pid = conn.pid
            try:
                proc = psutil.Process(pid)
                logger.info(f"Found process {proc.name()} with PID {
                            pid} occupying port {port}")
                proc.terminate()
                proc.wait()
                logger.info(f"Process with PID {pid} terminated.")
                return
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logger.error(f"Error killing process: {e}")
    logger.info(f"No process found occupying port {port}.")


# Flask 应用
app = Flask(__name__)

# 共享变量和锁
current_angle = 100
current_distance = 0
data_lock = Lock()

# TCP 服务器配置
TCP_HOST = '0.0.0.0'
TCP_PORT = 5005

# WebSocket 服务器配置
WS_HOST = '0.0.0.0'
WS_PORT = 5006
websocket_clients = set()

# 全局事件循环
loop = None

# 更新共享数据


def set_data(a, b):
    global current_angle, current_distance
    with data_lock:
        current_angle = a
        current_distance = b

# WebSocket 处理器


async def websocket_handler(websocket):
    logger.info(f"New WebSocket connection from {websocket.remote_address}")
    websocket_clients.add(websocket)
    try:
        async for message in websocket:
            logger.info(f"Received message: {message}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        websocket_clients.remove(websocket)
        logger.info(f"WebSocket connection closed for {
                    websocket.remote_address}")

# 广播数据给所有 WebSocket 客户端


async def broadcast_data():
    global current_angle, current_distance
    data = json.dumps({'angle': current_angle, 'distance': current_distance})
    logger.info(f"Broadcasting data: {data}")
    await send_to_all_clients(data)

# 处理 TCP 客户端连接


def handle_client(client_socket, addr):
    global current_angle, current_distance, loop
    logger.info(f"Connected to {addr}")

    try:
        while True:
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break

            logger.info(f"Received from {addr}: {data}")
            try:
                angle, distance = map(float, data.split(','))

                
                if angle > 270:
                    angle = 90-angle
                else:
                    angle=450-angle
                angle = angle-75
                
                if -360 <= angle <= 360:
                    set_data((angle), distance)
                    # 通过 WebSocket 广播数据
                    future = asyncio.run_coroutine_threadsafe(
                        broadcast_data(), loop)
                    future.result()  # 等待任务完成
                    client_socket.sendall(b"Data received\n")
                else:
                    client_socket.sendall(b"Invalid angle\n")
            except ValueError:
                client_socket.sendall(b"Invalid format\n")
    except Exception as e:
        logger.error(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()
        logger.info(f"Connection to {addr} closed.")

# 启动 TCP 服务器


def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    kill_process_by_port(TCP_PORT)
    server.bind((TCP_HOST, TCP_PORT))
    server.listen(5)
    logger.info(f"TCP Server listening on {TCP_HOST}:{TCP_PORT}")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(
            client_socket, addr), daemon=True).start()

# 发送消息给所有 WebSocket 客户端


async def send_to_all_clients(message):
    if websocket_clients:
        await asyncio.gather(*(client.send(message) for client in websocket_clients), return_exceptions=True)

# 启动 WebSocket 服务器


async def start_websocket_server():
    async with websockets.serve(websocket_handler, WS_HOST, WS_PORT):
        logger.info(f"WebSocket server started on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()  # 保持服务器运行

# 运行 WebSocket 服务器的事件循环


def run_websocket_server():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server())
    loop.run_forever()

# Flask 路由


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_angle', methods=['GET'])
def get_angle():
    with data_lock:
        return jsonify({'angle': current_angle, 'distance': current_distance})


if __name__ == '__main__':
    # 启动 WebSocket 服务器
    websocket_thread = threading.Thread(
        target=run_websocket_server, daemon=True)
    websocket_thread.start()

    # 启动 TCP 服务器
    tcp_thread = threading.Thread(target=tcp_server, daemon=True)
    tcp_thread.start()

    # 启动 Flask 服务器
    app.run(debug=True, host="0.0.0.0", port=5000)
