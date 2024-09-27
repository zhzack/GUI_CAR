import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
import sys

class CarPath(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Car Path Simulation')
        self.setGeometry(100, 100, 800, 600)
        self.path_points = self.generate_path()
        self.current_index = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.move_car)
        self.timer.start(100)  # 每100毫秒更新一次

    def generate_path(self):
        points = []
        # S曲线
        for x in np.linspace(0, 40, 100):
            y = 2 * np.sin((np.pi / 20) * x) + 2  # S曲线
            points.append((x, y))

        # 半圆
        for angle in np.linspace(0, np.pi, 100):
            x = 40 + 2 * np.cos(angle)
            y = 4 + 2 * np.sin(angle)
            points.append((x, y))

        # 从（40，4）到（0，4）
        for x in np.linspace(40, 0, 100):
            points.append((x, 4))

        return points

    def move_car(self):
        if self.current_index < len(self.path_points) - 1:  # 让小车沿路径移动
            self.current_index += 1
        else:
            self.current_index = 0  # 循环移动

        self.update()  # 更新绘制内容

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # 绘制路径
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200), 2))
        for i in range(1, len(self.path_points)):
            start_point = QtCore.QPointF(self.path_points[i-1][0], self.path_points[i-1][1])
            end_point = QtCore.QPointF(self.path_points[i][0], self.path_points[i][1])
            painter.drawLine(start_point, end_point)

        # 绘制小车
        if self.current_index < len(self.path_points):
            car_pos = self.path_points[self.current_index]
            painter.setBrush(QtGui.QColor(255, 0, 0))
            painter.drawRect(float(car_pos[0]) - 2, float(car_pos[1]) - 2, 4, 4)  # 小车为一个小方块

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CarPath()
    window.show()
    sys.exit(app.exec_())
