import sys
from PyQt5.QtWidgets import QApplication
from multiprocessing import Process, Queue
from main_window import MainWindow
import matplotlib.pyplot as plt
import key_trajectory

import tcp_server
import math
import socket
import requests
import aiohttp
import asyncio
import time

# 用于实时绘制折线图的线程


def plot_data_from_queue(pdoa_queue):
    # 初始化图表
    fig, ax = plt.subplots()
    pdoa1_data = []
    pdoa2_data = []
    pdoa3_data = []

    ax.set_xlabel('Time')
    ax.set_ylabel('PDOA Values')
    ax.set_title('实时 PDOA 折线图')

    # 绘制三条折线
    pdoa1_line, = ax.plot([], [], label="PDOA1")
    pdoa2_line, = ax.plot([], [], label="PDOA2")
    pdoa3_line, = ax.plot([], [], label="PDOA3")
    ax.legend()

    # 设置图表的限制
    ax.set_xlim(0, 3266)  # 假设 x 的范围在 0 到 50 之间
    ax.set_ylim(-300, 300)  # 假设 y 的范围在 0 到 100 之间

    while True:
        # 如果队列里有新的数据，则更新图表

        if not pdoa_queue.empty():
            pdoa1, pdoa2, pdoa3 = pdoa_queue.get()

            # 将新数据添加到列表
            pdoa1_data.append(pdoa1)
            pdoa2_data.append(pdoa2)
            pdoa3_data.append(pdoa3)

            # 只保留最近的 50 个数据点（可以根据需要调整）
            # if len(pdoa1_data) > 500:
            #     pdoa1_data.pop(0)
            #     pdoa2_data.pop(0)
            #     pdoa3_data.pop(0)
            if len(pdoa1_data) > 3266:
                # 更新三条折线的数据
                pdoa1_line.set_data(range(len(pdoa1_data)), pdoa1_data)
                pdoa2_line.set_data(range(len(pdoa2_data)), pdoa2_data)
                pdoa3_line.set_data(range(len(pdoa3_data)), pdoa3_data)

                # 更新图表显示
                plt.draw()
                plt.pause(0.1)  # 添加 pause，以便更新图表
            else:
                print(len(pdoa1_data))


def calculate_angle(x2, y2):

    x1 = 90
    y1 = 210
    # 使用 atan2 计算角度，返回值是弧度
    angle_rad = math.atan2(y2 - y1, x2 - x1)
    # 将角度转换为度数
    angle_deg = math.degrees(angle_rad)
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg


def tcp_client(data_queue, server_ip="127.0.0.1", server_port=5007, reconnect_delay=5):
    """TCP 客户端，支持自动重连"""
    while True:
        try:
            print(f"Connecting to {server_ip}:{server_port}...")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((server_ip, server_port))
            print("Connected!")
            while True:
                if not data_queue.empty():
                    data = data_queue.get()
                    # 生成角度和距离数据
                    angle = int(data['angle'])  # 角度范围 [0, 360)
                    distance = int(data['distance'])  # 距离范围 [0, 100)
                    message = f"{angle},{distance}\n"

                    # 发送数据
                    client.sendall(message.encode())
                    # print(f"Sent: {message.strip()}")

                    # # 接收服务器响应
                    # response = client.recv(1024).decode().strip()
                    # print(f"Server: {response}")

                    # time.sleep(0.2)  # 每 2 秒发送一次

        except (socket.error, ConnectionResetError, BrokenPipeError) as e:
            print(f"Connection lost: {e}")
            print(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)  # 等待后重连
        finally:
            try:
                client.close()
            except:
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 创建一个队列用于跨进程通信
    queue = Queue()
    data_queue = Queue()
    pdoa_queue = Queue()

    # 创建生成轨迹的子进程
    trajectory_process = Process(
        target=key_trajectory.generate_key_trajectory, args=(queue,))
    # trajectory_process = Process(target=key_trajectory.read_csv_and_put_in_queue, args=(queue,pdoa_queue))
    trajectory_process.start()

    http_send_data_process = Process(target=tcp_client, args=(data_queue,))
    http_send_data_process.start()

    # 启动异步任务（需要事件循环）
    #

    # 创建线程来实时绘制图表
    # plot_process = Process(target=plot_data_from_queue, args=(pdoa_queue,))
    # plot_process.start()

    # 创建 TCP 服务进程
    tcp_process = Process(target=tcp_server.tcp_server, args=(queue,))
    tcp_process.start()

    # 创建主窗口并传递队列
    window = MainWindow(queue, data_queue)
    window.show()

    try:
        sys.exit(app.exec_())
    finally:
        # 退出时终止子进程
        trajectory_process.terminate()
        trajectory_process.join()
        # plot_process.terminate()
        # plot_process.join()
        http_send_data_process.terminate()
        http_send_data_process.join()

        tcp_process.terminate()
        tcp_process.join()
