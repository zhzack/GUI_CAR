import socket
import threading
import time
from communication_interface import CommunicationInterface  # 导入抽象接口类


class TCPServerManager(CommunicationInterface):
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_sockets = []  # 存储所有的客户端连接
        self.stop_flag = False  # 控制服务器停止的标志
        self.thread = None  # 接受客户端连接的线程

    def start(self):
        """启动 TCP 服务端"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # 最大允许 5 个连接
        print(f"服务器启动，监听 {self.host}:{self.port}...")

        # 启动接受客户端连接的线程
        self.thread = threading.Thread(target=self.accept_connections)
        self.thread.start()

    def stop(self):
        """停止服务器，关闭所有连接"""
        print("正在关闭服务器...")
        self.stop_flag = True
        if self.thread:
            self.thread.join()  # 等待接受连接的线程结束
        for client_socket in self.client_sockets:
            self.close_connection(client_socket)
        if self.server_socket:
            self.server_socket.close()
        print("服务器已关闭")

    def accept_connections(self):
        """接受客户端连接并创建新的线程处理每个客户端"""
        while not self.stop_flag:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"新的客户端连接：{client_address}")
                self.client_sockets.append(client_socket)

                # 启动一个新的线程来处理该客户端
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                if not self.stop_flag:
                    print(f"接受客户端连接时发生错误: {e}")

    def handle_client(self, client_socket, client_address):
        """处理客户端的连接"""
        try:
            while not self.stop_flag:
                data = self.receive_data(client_socket)
                if not data:
                    break  # 如果没有数据，表示连接关闭

                print(f"收到来自 {client_address} 的数据: {data}")
                # 返回给客户端
                # self.send_data(client_socket, f'数据接收成功: {data}')
                self.send_data( f'数据接收成功: {data}')

                # 可以在这里将接收到的数据广播给其他客户端
                self.broadcast(data, client_socket)

        except Exception as e:
            print(f"与 {client_address} 的连接发生错误: {e}")
        finally:
            self.close_connection(client_socket)

    # def send_data(self, client_socket, data):
    #     """实现 CommunicationInterface 中的 send_data 方法"""
    #     try:
    #         client_socket.sendall(f'{data}\r\n'.encode('utf-8'))
    #         print(f"发送到 {client_socket.getpeername()}: {data}")
    #     except Exception as e:
    #         print(f"发送到客户端失败: {e}")
    #         self.close_connection(client_socket)

    def receive_data(self, client_socket):
        """实现 CommunicationInterface 中的 receive_data 方法"""
        try:
            data = client_socket.recv(1024)  # 接收最大1024字节的数据
            return data.decode('utf-8').strip() if data else None
        except Exception as e:
            print(f"接收来自 {client_socket.getpeername()} 的数据失败: {e}")
            self.close_connection(client_socket)
            return None

    def close_connection(self, client_socket):
        """关闭与客户端的连接"""
        try:
            if client_socket in self.client_sockets:
                self.client_sockets.remove(client_socket)
            client_socket.close()
            print(f"与 {client_socket.getpeername()} 的连接已关闭")

        except Exception as e:
            print(f"关闭与客户端连接失败: {e}")

    def broadcast(self, message, sender_socket):
        """广播消息给所有客户端"""
        for client_socket in self.client_sockets:
            if client_socket != sender_socket:  # 不发送给发送者
                try:
                    self.send_data( message)
                except Exception as e:
                    print(f"发送到 {client_socket.getpeername()} 失败: {e}")
                    self.close_connection(client_socket)

    def send_data(self, message):
        """广播消息给所有客户端"""
        sender_socket = None
        for client_socket in self.client_sockets:
            if client_socket != sender_socket:  # 不发送给发送者
                try:
                    self.send_data( message)
                except Exception as e:
                    print(f"发送到 {client_socket.getpeername()} 失败: {e}")
                    self.close_connection(client_socket)

    def close(self):
        """关闭服务端"""
        self.stop()


if __name__ == "__main__":
    # 创建 TCP 服务器并启动
    server = TCPServerManager()
    server.start()
    index = 0
    try:
        while True:
            time.sleep(0.01)  # 保持服务器运行
            message = f"{index}"
            server.broadcast(message, None)
            index = index+1
    except KeyboardInterrupt:
        server.stop()  # 手动停止服务器
