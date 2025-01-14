# tcp_server.py

import socket
import json
import threading
from multiprocessing import Queue

import socket
import subprocess
import os
import signal
import time


def kill_process_using_port(port):
    try:
        # 使用 netstat 命令查找占用端口的 PID
        result = subprocess.run(
            ['netstat', '-ano'], capture_output=True, text=True
        )
        # 查找端口所在的行
        for line in result.stdout.splitlines():
            if f':{port} ' in line:
                # 解析出 PID
                pid = line.split()[-1]
                print(f"找到占用端口 {port} 的进程 PID: {pid}")
                # 使用 taskkill 命令结束该进程
                subprocess.run(['taskkill', '/PID', pid, '/F'])
                print(f"进程 {pid} 已被终止.")
                return True
        print(f"没有找到占用端口 {port} 的进程.")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False


def tcp_server(queue, port=8080):
    # 首先检查并关闭占用端口的进程
    if kill_process_using_port(port):
        # 等待端口释放
        time.sleep(1)  # 可以根据实际情况调整等待时间

    # 创建 TCP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 尝试绑定端口
        server_socket.bind(('0.0.0.0', port))  # 监听所有接口和指定端口
        server_socket.listen(5)
        print(f"TCP 服务已启动，等待客户端连接...（端口 {port}）")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"客户端 {client_address} 已连接.")
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, queue))
            client_thread.start()

    except OSError as e:
        print(f"绑定端口失败: {e}")
    finally:
        server_socket.close()  # 确保程序退出时关闭套接字
        print("TCP 服务已关闭.")


def handle_client(client_socket, queue):
    buffer = b''
    try:
        while True:
            # 接收客户端发送的数据（最多 1024 字节）
            data = client_socket.recv(1024)
            if not data:
                continue
            # print(data)
            buffer += data
            while b' ' in buffer:
                packet_end = buffer.index(b' ') + 1
                packet = buffer[:packet_end]  # 解码为字符串
                buffer = buffer[packet_end:]  # 剩余的数据
                # print(packet)
                packet = packet.decode('utf-8')

                packet.replace('"',"")
                packet.replace(' ',"")
                parts = packet.split(',')
                parsed_data = {}
                # 第一个元素作为主键（比如 'BLE'）
                key = parts[0]
                
                print(parts)

                # 其他元素转换为数字，映射到 'x' 和 'y'
                x, y ,isTrue= map(int, parts[1:4])  # 假设只有 x, y 两个值
                if isTrue:
                    # 构造字典
                    parsed_data[key] = {'x': x, 'y': y}
                    # print(parsed_data)
                    queue.put([parsed_data])
            # 解析数据
            # try:
            #     # 假设数据是 JSON 格式
            #     json_data = data.decode('utf-8')
            #     data_dict = json.loads(json_data)
            #     # print(f"接收到数据: {data_dict}")

            #     # 处理数据并放入队列
            #     queue.put([data_dict])
            # except json.JSONDecodeError:
            #     print("接收到的不是有效的 JSON 数据.")
            #     pass

    except Exception as e:
        print(f"处理客户端数据时发生错误: {e}")
    finally:
        # 客户端断开连接
        client_socket.close()
        print("客户端连接已关闭.")
