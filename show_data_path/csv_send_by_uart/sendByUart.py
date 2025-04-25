import serial
import time
from tkinter import filedialog

# 配置项
SERIAL_PORT = 'COM35'      # 串口名称，Linux下一般是 /dev/ttyUSB0 或 /dev/ttyS0
BAUD_RATE = 234000          # 波特率
FILE_PATH = 'D:/ZhengZ/code/GUI_CAR/show_data_path/2025年4月11日/绕圈不停顿-前145后146-i高度77-距离85_order2.txt'   # 要读取的文件路径
# FILE_PATH = 'D:/ZhengZ/code/GUI_CAR/show_data_path/2025年4月11日/绕圈不停顿-前145后146-i高度77-距离93_order.txt'   # 要读取的文件路径
# FILE_PATH = 'D:/ZhengZ/code/py_data/Data/20250409/2025年4月9日新板子/data_122017_tx2rxa_new_0034.txt'   # 要读取的文件路径
# FILE_PATH = 'D:/ZhengZ/code/py_data/Data/20250409/2025年4月9日新板子/data_122415_tx2rxa_new_0031.txt'   # 要读取的文件路径
# FILE_PATH = 'D:/ZhengZ/code/py_data/Data/20250409/新换芯片板子_绕圈加拉距/data_143239_car_1.csv'   # 要读取的文件路径
FILE_PATH = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.txt")])
DELAY_MS = 10             # 每行之间的发送间隔（毫秒）


def send_file_to_serial(file_path, port, baudrate, delay_ms):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"打开串口 {port} 成功，开始发送文件内容...")

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    ser.write((line + '\n').encode('utf-8'))
                    print(f"已发送: {line}")
                    time.sleep(delay_ms / 1000.0)

        ser.close()
        print("发送完成，串口已关闭。")

    except Exception as e:
        print(f"出错：{e}")


if __name__ == "__main__":
    send_file_to_serial(FILE_PATH, SERIAL_PORT, BAUD_RATE, DELAY_MS)
