import socket
import threading
import time
from communication_interface import CommunicationInterface

# 配置服务器的IP地址和端口号
HOST = '0.0.0.0'  # 监听所有可用的网络接口
PORT = 8888        # 端口号

# 客户端管理类，包含每个客户端连接的心跳功能


class ClientHandler(threading.Thread,CommunicationInterface):
    
    def __init__(self, client_socket, client_address):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.running = True  # 用来控制是否持续发送心跳
        self.start()

    def run(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024)  # 接收最大1024字节的数据
                if not data:
                    break  # 如果没有数据，结束循环

                print(f"收到来自 {self.client_address} 的数据: {
                      data.decode('utf-8')}")
                # 发送响应
                self.client_socket.sendall('数据接收成功'.encode('utf-8'))
        except Exception as e:
            print(f"连接 {self.client_address} 错误: {e}")
            self.stop()  # 数据接收失败时清理连接
        finally:
            if self.running:
                self.client_socket.close()
            print(f"与 {self.client_address} 的连接已关闭")

    def send_heartbeat(self):
        # 定时每秒钟向客户端发送心跳包
        index = 0
        while self.running:
            try:
                self.client_socket.sendall(
                    f'心跳{index}!'.encode('utf-8'))  # 发送心跳
                print(f"{index}发送心跳到 {self.client_address}")
                index = index+1
                time.sleep(0.1)  # 每秒发送一次
            except Exception as e:
                print(f"发送心跳到 {self.client_address} 失败: {e}")
                self.stop()  # 发送失败时停止连接
                break

    def stop(self):
        self.running = False
        try:
            self.client_socket.close()
        except Exception as e:
            print(f"关闭连接失败: {e}")
        print(f"已清除与 {self.client_address} 的连接")


def start_tcp_server():
    # 创建一个 TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # 绑定IP地址和端口
        server_socket.bind((HOST, PORT))

        # 开始监听，最大允许5个连接请求
        server_socket.listen(5)
        print(f"服务器启动，监听 {HOST}:{PORT}...")

        while True:
            # 等待接入的客户端连接
            client_socket, client_address = server_socket.accept()
            print(f"连接来自 {client_address}")

            # 为每个客户端创建一个处理线程
            client_handler = ClientHandler(client_socket, client_address)

            # 启动一个心跳线程
            threading.Thread(
                target=client_handler.send_heartbeat, daemon=True).start()


if __name__ == "__main__":
    start_tcp_server()
