import socket
import csv
import time

# 连接到服务器


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

# 构造发送的包格式：'key,x,y,isTrue'


def send_data(client_socket, key, x, y, isTrue):
    message = f"{key},{x},{y},{isTrue} "
    # 发送数据到服务器
    client_socket.sendall(message.encode('utf-8'))
    print(f"Sent: {message}")

# 读取 CSV 文件并返回数据


def read_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # 假设 CSV 格式是：time,x,y
            time_value, x, y = row
            # 这里假设时间是以秒为单位的数值
            data.append((float(time_value), int(x), int(y)))
    return data

# 主程序


def main():
    # 服务器地址和端口
    host = '127.0.0.1'
    port = 8080

    # 连接到服务器
    client_socket = connect_to_server(host, port)

    # 读取 CSV 文件数据
    csv_file = 'data.csv'  # 替换为实际 CSV 文件路径
    data = read_csv(csv_file)

    # 获取数据的总长度
    total_lines = len(data)

    try:
        # 初始的时间
        start_time = time.time()

        # 依次发送 CSV 文件中的每一行数据
        key = "ggg"
        for index, (time_value, x, y) in enumerate(data):
            # 计算时间间隔
            elapsed_time = time.time() - start_time
            if elapsed_time < time_value:
                # 如果时间未到达当前行的时间，休眠
                time.sleep(time_value - elapsed_time)
            # 每行发送数据

            isTrue = 1  # 假设 isTrue 为 1
            send_data(client_socket, key, x, y, isTrue)
        send_data(client_socket, key, 0, 0, 0)
    except KeyboardInterrupt:
        print("Client stopped.")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
