from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

class AutoClosePopup(QWidget):
    def __init__(self, parent, message, duration=2000):
        """
        :param parent: 父窗口（主窗口）
        :param message: 显示的文字
        :param duration: 弹窗显示时间（毫秒），默认 2 秒
        """
        super().__init__(parent)

        # 设置弹窗无边框
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)

        # 设置弹窗背景颜色和文字样式
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 10px;
            font-size: 14px;
            padding: 10px;
        """)

        # 创建布局和文字
        layout = QVBoxLayout(self)
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # 设置布局
        self.setLayout(layout)

        # 调整窗口大小以适应内容
        self.adjustSize()

        # 将弹窗放置到主窗口中心
        self.center_in_parent()

        # 定时器，用于自动关闭弹窗
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)
        self.timer.start(duration)

    def center_in_parent(self):
        """将弹窗放置到主窗口中心"""
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.x() + (parent_rect.width() - self.width()) // 2,
                parent_rect.y() + (parent_rect.height() - self.height()) // 2,
            )
