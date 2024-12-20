import serial
import serial.tools.list_ports
import threading
import time
from communication_interface import CommunicationInterface  # 导入抽象接口类


class SerialManager(CommunicationInterface):
    def __init__(self, default_baudrate=115200):
        self.port = None
        self.baudrate = default_baudrate
        self.serial_conn = None

        # 创建停止标志
        self.stop_flag = False
        # 创建线程
        self.thread = threading.Thread(target=self.receive_data_while)
        # 启动线程
        self.thread.start()

    def scan_ports(self):
        """
        扫描可用的串口并返回端口列表
        """
        ports = serial.tools.list_ports.comports()
        available_ports = [port.device for port in ports]
        return available_ports

    def stop_thread(self):
        """设置停止标志，停止线程循环"""
        self.stop_flag = True
        self.thread.join()

    def match_port_by_keyword(self, keyword):
        """
        根据关键字匹配串口名称
        :param keyword: 端口名称关键字，例如 'USB'
        """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if keyword in port.description or keyword in port.device:
                print(f"匹配到端口: {port.device}")
                return port.device
        print("未找到匹配的端口")
        return None

    def set_port(self, port):
        """
        设置串口
        :param port: 串口名称
        """
        self.port = port

    def set_baudrate(self, baudrate):
        """
        设置波特率
        :param baudrate: 波特率值
        """
        self.baudrate = baudrate

    def connect(self):
        """
        连接到串口
        """
        if not self.port:
            raise ValueError("未设置串口端口")
        self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
        print(f"已连接到串口 {self.port}，波特率 {self.baudrate}")

    def disconnect(self):
        """
        断开串口连接
        """
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("串口连接已关闭")
        # 在主程序退出时，停止接收线程
        self.stop_thread()

    def send_data(self, data):
        """
        发送数据到串口
        :param data: 需要发送的字符串
        """
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f'{data}\r\n'.encode('utf-8'))
        else:
            raise ConnectionError("串口未打开")

    def receive_data(self):
        """
        接收串口返回的数据
        :return: 返回的数据字符串
        """
        if self.serial_conn and self.serial_conn.is_open:
            return self.serial_conn.readline().decode('utf-8').strip()
        return ""

    def receive_data_while(self):
        """持续接收串口数据"""
        while not self.stop_flag:
            print(self.receive_data())
            time.sleep(0.05)

    def close(self):
        """关闭串口"""
        self.disconnect()
        
