from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QIcon

class CarKeyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化主界面
        self.setWindowTitle("汽车钥匙功能展示")
        self.setGeometry(200, 200, 400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # 创建窗口容器
        container = QWidget(self)
        self.setCentralWidget(container)

        # 设置布局
        layout = QVBoxLayout(container)

        # 车图标显示区域
        self.car_icon = QLabel(self)
        self.car_icon.setAlignment(Qt.AlignCenter)
        self.car_icon.setPixmap(QIcon("car_image.png").pixmap(100, 100))  # 假设有一张汽车图标
        layout.addWidget(self.car_icon)

        # 创建按钮
        button_layout = QHBoxLayout()

        self.lock_button = QPushButton("锁车", self)
        self.unlock_button = QPushButton("解锁", self)
        self.start_button = QPushButton("启动", self)
        self.window_button = QPushButton("车窗", self)

        self.lock_button.clicked.connect(self.lock_car)
        self.unlock_button.clicked.connect(self.unlock_car)
        self.start_button.clicked.connect(self.toggle_start_stop)
        self.window_button.clicked.connect(self.toggle_window)

        button_layout.addWidget(self.lock_button)
        button_layout.addWidget(self.unlock_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.window_button)

        layout.addLayout(button_layout)

        # 状态显示
        self.status_label = QLabel("钥匙电池：正常", self)
        layout.addWidget(self.status_label)

        # 电池状态定时更新
        self.battery_timer = QTimer(self)
        self.battery_timer.timeout.connect(self.update_battery_status)
        self.battery_timer.start(5000)  # 每5秒更新一次电池状态

        # 控制状态
        self.car_locked = False
        self.car_started = False
        self.window_open = False

    def lock_car(self):
        """锁车功能"""
        self.car_locked = True
        self.car_icon.setPixmap(QIcon("car_locked_image.png").pixmap(100, 100))  # 使用锁定的汽车图标
        self.status_label.setText("车门已锁定")

    def unlock_car(self):
        """解锁车功能"""
        self.car_locked = False
        self.car_icon.setPixmap(QIcon("car_unlocked_image.png").pixmap(100, 100))  # 使用解锁的汽车图标
        self.status_label.setText("车门已解锁")

    def toggle_start_stop(self):
        """启动/熄火功能"""
        if self.car_started:
            self.car_started = False
            self.status_label.setText("汽车已熄火")
        else:
            self.car_started = True
            self.status_label.setText("汽车已启动")

    def toggle_window(self):
        """车窗控制功能"""
        if self.window_open:
            self.window_open = False
            self.status_label.setText("车窗已关闭")
        else:
            self.window_open = True
            self.status_label.setText("车窗已打开")

    def update_battery_status(self):
        """模拟电池状态变化"""
        import random
        battery_status = random.choice(["正常", "电量低", "电量不足"])
        self.status_label.setText(f"钥匙电池：{battery_status}")

if __name__ == "__main__":
    app = QApplication([])
    window = CarKeyApp()
    window.show()
    app.exec_()
