import socket
import threading
from abc import ABC, abstractmethod
from communication_interface import CommunicationInterface  # 导入抽象接口类


class TCPServer(CommunicationInterface):
    def __init__(self, host='0.0.0.0', port=80):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = []  # 存储所有已连接的客户端
        self.running = True

        self.lock = threading.Lock()  # 用于线程安全
        print(f"Server started on {self.host}:{self.port}")

        # 启动接受连接的线程
        self.accept_thread = threading.Thread(
            target=self._accept_clients, daemon=True)
        self.accept_thread.start()

    def _accept_clients(self):
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"Client connected: {client_address}")

                with self.lock:
                    self.clients.append(client_socket)

                threading.Thread(target=self._handle_client, args=(
                    client_socket,), daemon=True).start()
            except socket.error as e:
                print(f"Error accepting clients: {e}")

    def _handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                # 尝试解码，如果失败则处理异常
                try:
                    print(f"Received: {data.decode('utf-8')
                                       } from {client_socket.getpeername()}")
                except UnicodeDecodeError:
                    print(
                        f"Received non-UTF-8 data from {client_socket.getpeername()}")

            except socket.error:
                break

        with self.lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
                print(f"Client disconnected: {client_socket.getpeername()}")
        client_socket.close()

    def send_data(self, data: str):
        with self.lock:
            for client in self.clients:
                try:
                    client.sendall(data.encode('utf-8'))
                    print(data)

                except socket.error as e:
                    print(f"Error sending to {client.getpeername()}: {e}")

    def receive_data(self):
        # 这里在 _handle_client 方法中处理接收到的消息
        pass  # 此方法实际不需要实现，消息已经在后台处理

    def close(self):
        print("Closing server...")
        self.running = False
        with self.lock:
            for client in self.clients:
                try:
                    client.close()
                except socket.error as e:
                    print(f"Error closing client socket: {e}")
            self.clients.clear()
        self.server_socket.close()
        print("Server closed.")


# 示例用法
if __name__ == "__main__":
    server = TCPServer(host='0.0.0.0', port=80)
    try:
        while True:
            msg = input("Enter message to broadcast (type 'exit' to stop): ")
            if msg.lower() == 'exit':
                break
            server.send_data(msg)
    finally:
        server.close()
