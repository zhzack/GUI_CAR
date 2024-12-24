import sys
import math
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow


class LightingApp(QMainWindow):
    def __init__(self, trajectory_points, num_lights):
        super().__init__()
        self.setWindowTitle("Lighting Control - Precomputed Angles")
        self.setGeometry(100, 100, 600, 600)

        # 配置灯的参数
        self.origin = QPointF(300, 300)  # 原点
        self.trajectory = trajectory_points  # 原始轨迹点
        self.num_lights = num_lights  # 灯的总数
        self.lights = self.distribute_lights_uniformly()  # 均匀分布灯的位置
        self.light_angles = self.precompute_angles()  # 预计算灯的角度
        self.active_light = -1  # 当前亮的灯的索引

        self.setMouseTracking(True)  # 启用鼠标移动事件

    def calculate_trajectory_length(self):
        """计算轨迹的总长度"""
        total_length = 0
        for i in range(len(self.trajectory) - 1):
            start = self.trajectory[i]
            end = self.trajectory[i + 1]
            segment_length = math.hypot(end.x() - start.x(), end.y() - start.y())
            total_length += segment_length
        return total_length

    def distribute_lights_uniformly(self):
        """根据总灯数均匀分布灯的位置"""
        total_length = self.calculate_trajectory_length()
        segment_lengths = []
        for i in range(len(self.trajectory) - 1):
            start = self.trajectory[i]
            end = self.trajectory[i + 1]
            segment_length = math.hypot(end.x() - start.x(), end.y() - start.y())
            segment_lengths.append(segment_length)

        # 每个灯的间隔长度
        light_spacing = total_length / (self.num_lights - 1)

        # 逐段插值灯的位置
        lights = []
        current_length = 0  # 距离起点的累计长度
        for i in range(len(self.trajectory) - 1):
            start = self.trajectory[i]
            end = self.trajectory[i + 1]
            segment_length = segment_lengths[i]

            while current_length <= segment_length:
                t = current_length / segment_length
                x = start.x() + t * (end.x() - start.x())
                y = start.y() + t * (end.y() - start.y())
                lights.append(QPointF(x, y))

                current_length += light_spacing

            current_length -= segment_length  # 剩余长度进入下一段

        # 确保灯的总数正确
        lights.append(self.trajectory[-1])
        return lights[:self.num_lights]

    def precompute_angles(self):
        """预计算每个灯与原点的角度"""
        angles = []
        for light in self.lights:
            dx = light.x() - self.origin.x()
            dy = self.origin.y() - light.y()  # 注意坐标系方向
            angle = math.atan2(dy, dx)
            degree = math.degrees(angle)
            angles.append(degree if degree >= 0 else degree + 360)
        return angles

    def calculate_angle(self, mouse_pos):
        """计算鼠标与原点的夹角"""
        dx = mouse_pos.x() - self.origin.x()
        dy = self.origin.y() - mouse_pos.y()  # 注意坐标系方向
        angle = math.atan2(dy, dx)  # 计算弧度
        degree = math.degrees(angle)  # 转换为角度
        return degree if degree >= 0 else degree + 360

    def find_active_light(self, angle):
        """根据角度找到最接近连线的灯的索引"""
        min_distance = float('inf')
        active_light = -1

        for i, light_angle in enumerate(self.light_angles):
            distance = abs(light_angle - angle)
            if distance < min_distance:
                min_distance = distance
                active_light = i

        return active_light

    def mouseMoveEvent(self, event):
        """鼠标移动事件，更新当前激活的灯"""
        angle = self.calculate_angle(event.pos())
        self.active_light = self.find_active_light(angle)
        self.update()  # 触发重绘

    def paintEvent(self, event):
        """绘制轨迹和灯"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制轨迹
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        for i in range(len(self.trajectory) - 1):
            painter.drawLine(self.trajectory[i], self.trajectory[i + 1])

        # 绘制灯
        for i, point in enumerate(self.lights):
            color = QColor(255, 0, 0) if i == self.active_light else QColor(200, 200, 200)
            painter.setBrush(color)
            painter.drawEllipse(point.toPoint(), 5, 5)  # 绘制灯的小圆点

        painter.end()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 定义不规则轨迹的点
    trajectory_points = [
        QPointF(150, 150), QPointF(200, 120), QPointF(300, 100),
        QPointF(400, 150), QPointF(450, 250), QPointF(400, 350),
        QPointF(300, 400), QPointF(200, 350), QPointF(150, 250)
    ]

    window = LightingApp(trajectory_points, num_lights=50)  # 设置总灯数
    window.show()
    sys.exit(app.exec_())
