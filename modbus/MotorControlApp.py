from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QWidget, QPushButton,
    QLabel, QComboBox, QSpinBox, QTextEdit, QCheckBox
)
from serial.tools.list_ports import comports
from SerialHandler import SerialHandler
import sys


class MotorControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.serial_handler = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_status)
        self.slave_id = 1  # Default Modbus slave ID
        # 初始化 DICtronVal
        self.DICtronVal = 0
        self.bool = False

    def init_ui(self):
        self.setWindowTitle("电机控制")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        self.port_label = QLabel("选择COM端口：")
        layout.addWidget(self.port_label)

        self.cmb_ports = QComboBox()
        self.refresh_ports()
        layout.addWidget(self.cmb_ports)

        self.btn_connect = QPushButton("连接")
        self.btn_connect.clicked.connect(self.connect_serial)
        layout.addWidget(self.btn_connect)

        self.ckb_motor_enable = QCheckBox("电机使能")
        self.ckb_motor_enable.setEnabled(False)
        self.ckb_motor_enable.stateChanged.connect(self.toggle_motor)
        layout.addWidget(self.ckb_motor_enable)

        self.num_degree = QSpinBox()
        self.num_degree.setRange(0, 360)
        self.num_degree.setSuffix("°")
        # self.num_degree.setEnabled(False)
        layout.addWidget(QLabel("角度设置："))
        layout.addWidget(self.num_degree)

        self.num_speed = QSpinBox()
        self.num_speed.setRange(0, 60)
        self.num_speed.setSuffix("°/s")
        # self.num_speed.setEnabled(False)
        layout.addWidget(QLabel("速度设置："))
        layout.addWidget(self.num_speed)

        self.btn_inching = QPushButton("角度设置")
        # self.btn_inching.setEnabled(False)
        self.btn_inching.clicked.connect(self.start_inching)
        # self.btn_inching.released.connect(self.stop_inching)
        layout.addWidget(self.btn_inching)

        # # 向左转按钮
        # self.btn_left = QPushButton("向左转")
        # self.btn_left.setEnabled(True)
        # self.btn_inching.pressed.connect(self.start_left_move)
        # self.btn_inching.released.connect(self.stop_left_move)
        # layout.addWidget(self.btn_left)

        # # 向右转按钮
        # self.btn_right = QPushButton("向右转")
        # self.btn_right.setEnabled(True)
        # self.btn_inching.pressed.connect(self.start_right_move)
        # self.btn_inching.released.connect(self.stop_right_move)
        # layout.addWidget(self.btn_right)

        layout.addWidget(QLabel("日志："))
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        layout.addWidget(self.txt_log)

        layout.addWidget(QLabel("状态："))
        self.lbl_status = QLabel("未连接")
        layout.addWidget(self.lbl_status)

        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def refresh_ports(self):
        self.cmb_ports.clear()
        ports = comports()
        for port in ports:
            self.cmb_ports.addItem(port.device)

    def log(self, message):
        self.txt_log.append(message)

    def connect_serial(self):
        port = self.cmb_ports.currentText()
        if not port:
            QMessageBox.warning(self, "错误", "请选择COM端口！")
            return

        self.serial_handler = SerialHandler(port)
        if self.serial_handler.open():
            self.log("串口连接成功")
            self.lbl_status.setText("连接成功")
            self.ckb_motor_enable.setEnabled(True)
            self.btn_connect.setEnabled(False)
            self.timer.start(3000)  # 每秒刷新状态
        else:
            QMessageBox.critical(self, "错误", "无法连接到COM端口！")

    def toggle_motor(self, state):
        if not self.serial_handler:
            return

        if state:
            self.log("电机使能")
            self.serial_handler.write_single(
                self.slave_id, 0x04F, 0x0500)  # 使能指令
            # self.num_degree.setEnabled(True)
            # self.num_speed.setEnabled(True)
            # self.btn_inching.setEnabled(True)
        else:
            self.log("电机停止")
            self.serial_handler.write_single(
                self.slave_id, 0x04F, 0x0600)  # 停止指令
            # self.num_degree.setEnabled(False)
            # self.num_speed.setEnabled(False)
            # self.btn_inching.setEnabled(False)

    def start_left_move(self):
        self.DI_ctrol(4, True)
        print('self.DI_ctrol(4, True)')

    def stop_left_move(self):
        self.DI_ctrol(4, False)
        print('self.DI_ctrol(4, False)')

    def start_right_move(self):
        self.DI_ctrol(3, True)

    def stop_right_move(self):
        self.DI_ctrol(3, False)

    def start_inching(self):
        self.bool != self.bool
        # self.DI_ctrol(3, self.bool)
        if not self.serial_handler:
            return

        degree = self.num_degree.value()
        speed = self.num_speed.value()
        # serial.write(0x4a, 1); //绝对位置

        # serial.write32(0x50,  (int)(numDegree.Value/360*90000/2)); // H11_12 第1 段移动位移 指令单位
        # serial.write(0x52, (int)nmbRpm.Value*30); // H11_14 移最大运行速度

        # serial.write(0x16, 0x0c);// di5 位置路径触发
        # serial.write(0x17, 0x0e);// di6 路径地址0
        self.serial_handler.write_single(self.slave_id, 0x4a, 1)

        self.serial_handler.write_single(
            self.slave_id, 0x50, degree/360*90000/2)

        self.serial_handler.write_single(self.slave_id, 0x52, speed*30)
        self.serial_handler.write_single(self.slave_id, 0x16, 0x0c)
        self.serial_handler.write_single(self.slave_id, 0x17, 0x0e)

        self.log(f"点动开始，角度：{degree}°")

    

    def DI_ctrol(self, num, stat):
        print(self.DICtronVal)
        DICtronVal = self.DICtronVal
        # 设置指定的位
        if stat:
            DICtronVal |= (1 << num)  # 通过左移操作设置指定位置为 1
        else:
            DICtronVal &= ~(1 << num)  # 通过按位取反后清除指定位置为 0
        self.serial_handler.write_single(self.slave_id, 0x10, DICtronVal)

    def read_status(self):
        """
        读取电机状态，解析速度、位置、DO、DI、报警和状态信息。
        """
        if not self.serial_handler:
            return

        # 从地址 0x0004 读取 7 字节数据
        response = self.serial_handler.read_holding_registers(
            self.slave_id, 0x0004, 7)
        if response is None or len(response) < 7:
            self.log("状态读取失败：无效的响应")
            return

        # 反转字节序以匹配大端解析
        data = list(response)
        data.reverse()
        data = data[2:-3]

        print(' '.join(f'{byte:02x}' for byte in data))

        try:
            # 速度 (Int16) - 前两个字节
            speed = int.from_bytes(data[0:2], byteorder='little', signed=True)

            # 位置 (Int32) - 组合 16 位高字、16 位中字和低 16 位
            high_word = int.from_bytes(
                data[4:6], byteorder='little', signed=True)
            middle_word = int.from_bytes(
                data[2:4], byteorder='little', signed=False)
            position = (high_word << 16) | middle_word

            # 数字输出 (DO) - 第 6 字节
            DO = data[6]

            # 数字输入 (DI) - 第 8 字节
            DI = data[8]

            # 报警 - 第 10 字节
            alarm = data[10]

            # 状态 - 第 12 字节
            stat = data[12]

            # 格式化并显示状态
            status_text = (
                f"速度：{speed} 位置：{position} DO：{bin(DO)} "
                f"DI：{bin(DI)} 报警：{alarm} 状态：{bin(stat)}"
            )
            self.log(status_text)

            # 跟踪逻辑
            if self.trace_run_flag and (stat & 0x01):
                self.current_trace = not self.current_trace
                if self.current_trace:
                    self.trace0()
                else:
                    self.trace1()

        except Exception as e:
            self.log(f"状态解析失败：{e}")


if __name__ == "__main__":
    app = QApplication([])
    main_window = MotorControlApp()
    main_window.show()
    sys.exit(app.exec_())
