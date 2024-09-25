from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import Qt, QRect
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("浮动展示台示例")
        
        # 主布局
        self.layout = QVBoxLayout(self)
        
        # 标签示例
        self.coord_label = QLabel("X: 0, Y: 0", self)
        self.coord_label.setStyleSheet("QLabel { background-color : rgba(255, 255, 255, 0.5); padding: 5px; font-size: 20px; }")
        self.layout.addWidget(self.coord_label)
        
        # 创建浮动展示台
        self.float_widget = QLabel("浮动展示台\n展示一些数据", self)
        self.float_widget.setStyleSheet("QLabel { background-color : rgba(255, 255, 255, 0.8); padding: 10px; font-size: 18px; }")
        self.float_widget.setFixedWidth(150)  # 设置宽度
        self.float_widget.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.float_widget)
        
        # 更新浮动展示台的位置
        self.update_float_position()

    def resizeEvent(self, event):
        self.update_float_position()

    def update_float_position(self):
        # 计算浮动展示台的位置，固定在右上角
        x = self.width() - self.float_widget.width() - 10  # 右边距10
        y = 10  # 上边距10
        self.float_widget.setGeometry(QRect(x, y, self.float_widget.width(), self.float_widget.height()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.resize(800, 600)
    main_win.show()
    sys.exit(app.exec_())
