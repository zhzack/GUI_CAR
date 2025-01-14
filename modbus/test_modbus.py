import sys
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QMessageBox
import serial.tools.list_ports

# CRC16 计算函数 (Modbus RTU)
def calculate_crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

class ModbusRTUApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus RTU 控制")
        self.setGeometry(100, 100, 400, 350)  # 修改窗口高度
        
        # 初始化界面
        self.init_ui()

    def init_ui(self):
        # 串口选择下拉框
        self.port_label = QLabel("选择串口:")
        self.port_combo = QComboBox(self)
        self.populate_ports()

        # 波特率选择
        self.baud_label = QLabel("选择波特率:")
        self.baud_combo = QComboBox(self)
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])

        # 寄存器地址输入框
        self.address_label = QLabel("设备地址 (十六进制):")
        self.address_input = QLineEdit(self)

        # 功能码输入框
        self.function_code_label = QLabel("功能码 (十六进制):")
        self.function_code_input = QLineEdit(self)

        # 寄存器地址输入框
        self.register_address_label = QLabel("寄存器地址 (十六进制):")
        self.register_address_input = QLineEdit(self)

        # 发送值输入框
        self.value_label = QLabel("发送值 (十六进制):")
        self.value_input = QLineEdit(self)

        # 控制按钮
        self.send_button = QPushButton("发送 Modbus 命令", self)
        
        # 布局设置
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.port_label)
        form_layout.addWidget(self.port_combo)
        form_layout.addWidget(self.baud_label)
        form_layout.addWidget(self.baud_combo)
        form_layout.addWidget(self.address_label)
        form_layout.addWidget(self.address_input)
        form_layout.addWidget(self.function_code_label)
        form_layout.addWidget(self.function_code_input)
        form_layout.addWidget(self.register_address_label)
        form_layout.addWidget(self.register_address_input)
        form_layout.addWidget(self.value_label)
        form_layout.addWidget(self.value_input)
        form_layout.addWidget(self.send_button)

        self.setLayout(form_layout)

        # 连接按钮事件
        self.send_button.clicked.connect(self.send_modbus_command)

    def populate_ports(self):
        """ 自动扫描并列出所有串口 """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def send_modbus_command(self):
        """ 发送 Modbus RTU 命令 """
        try:
            # 获取用户输入的设备地址、功能码、寄存器地址和发送的值
            address = int(self.address_input.text(), 16)  # 转换为十六进制地址
            function_code = int(self.function_code_input.text(), 16)  # 转换为十六进制功能码
            register_address = int(self.register_address_input.text(), 16)  # 转换为十六进制寄存器地址
            value = int(self.value_input.text(), 16)  # 转换为十六进制值

            # 获取串口和波特率配置
            selected_port = self.port_combo.currentText()
            selected_baud = self.baud_combo.currentText()

            # 数据域：寄存器地址 + 写入值
            data = [register_address >> 8, register_address & 0xFF, value >> 8, value & 0xFF]

            # 构造 Modbus RTU 请求帧
            frame = [address, function_code] + data  # 地址 + 功能码 + 数据

            # 使用自定义的 CRC16 计算函数计算 CRC 校验码
            crc = calculate_crc16(frame)  # 计算 CRC16 校验码
            crc_low = crc & 0xFF
            crc_high = (crc >> 8) & 0xFF

            # 将 CRC 校验码添加到数据帧
            frame.append(crc_low)
            frame.append(crc_high)

            # 设置串口连接
            with serial.Serial(selected_port, int(selected_baud), timeout=1) as ser:
                # 发送 Modbus RTU 命令
                ser.write(bytes(frame))

                # 弹出成功消息框
                self.show_message("操作成功", f"已向设备 {hex(address)} 发送数据", QMessageBox.Information)

        except ValueError as e:
            self.show_message("错误", f"输入格式错误: {str(e)}", QMessageBox.Critical)
        except Exception as e:
            self.show_message("错误", f"发生异常: {str(e)}", QMessageBox.Critical)

    def show_message(self, title, message, icon):
        """ 显示消息框 """
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.exec_()

def main():
    app = QApplication(sys.argv)
    window = ModbusRTUApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
