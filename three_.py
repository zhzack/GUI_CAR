import sys
import math
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow


class LightingTrack:
    def __init__(self, points, leds_per_meter=144):
        self.points = points  # 轨迹点
        self.leds_per_meter = leds_per_meter  # 每米灯数
        self.lights = self.distribute_lights()  # 预计算灯的位置和角度

    def calculate_segment_length(self, start, end):
        """计算两个点之间的距离"""
        return math.hypot(end[0] - start[0], end[1] - start[1])

    def distribute_lights(self):
        """根据轨迹点计算灯的位置，并计算每个灯的角度"""
        lights = []
        total_length = 0  # 轨迹总长度
        segment_lengths = []

        # 计算每段的长度并记录
        for i in range(len(self.points) - 1):
            start = self.points[i]
            end = self.points[i + 1]
            segment_length = self.calculate_segment_length(start, end)
            segment_lengths.append(segment_length)
            total_length += segment_length

        # 每个灯之间的间隔
        light_spacing = total_length / \
            (self.leds_per_meter * (len(self.points) - 1))

        # 遍历每个轨迹段，将灯均匀分布
        current_length = 0  # 当前累积的长度
        for i in range(len(self.points) - 1):
            start = self.points[i]
            end = self.points[i + 1]
            segment_length = segment_lengths[i]

            while current_length <= segment_length:
                t = current_length / segment_length
                x = start[0] + t * (end[0] - start[0])
                y = start[1] + t * (end[1] - start[1])

                # 计算灯的角度
                dx = x
                dy = y
                angle = math.atan2(dy, dx)  # 计算弧度
                angle_deg = math.degrees(angle)  # 转换为角度
                if angle_deg < 0:
                    angle_deg += 360  # 确保角度在 0 到 360 之间

                lights.append((x, y, angle_deg))

                current_length += light_spacing

            current_length -= segment_length  # 移动到下一个轨迹段

        return lights

    def find_nearest_led(self, angle):
        """根据角度找到最接近的灯的ID"""
        min_distance = float('inf')
        nearest_led_id = -1

        for i, (x, y, light_angle) in enumerate(self.lights):
            distance = abs(light_angle - angle)
            if distance < min_distance:
                min_distance = distance
                nearest_led_id = i

        return nearest_led_id

    def get_center(self):
        """计算轨迹的中心"""
        x_sum, y_sum = 0, 0
        for x, y in self.points:
            x_sum += x
            y_sum += y
        return x_sum / len(self.points), y_sum / len(self.points)


class LightingApp(QMainWindow):
    def __init__(self, points, leds_per_meter=144):
        super().__init__()
        self.setWindowTitle("Lighting Control")
        
        # 设置全屏显示
        self.showFullScreen()

        # 创建轨迹
        self.track = LightingTrack(points, leds_per_meter)

        # 获取轨迹的中心作为原点
        self.origin = QPointF(*self.track.get_center())  # 原点在轨迹中心
        self.active_led_id = -1  # 当前活跃灯的ID
        self.scale_factor = 1.0  # 初始缩放比例
        self.offset = QPointF(0, 0)  # 用于平移的偏移量
        self.setMouseTracking(True)  # 启用鼠标移动事件

        self.last_pos = None  # 用于记录鼠标拖动的起始位置

    def calculate_angle(self, mouse_pos):
        """计算鼠标与原点的夹角"""
        dx = mouse_pos.x() - self.origin.x()
        dy = -(self.origin.y() - mouse_pos.y())  # 注意坐标系方向
        angle = math.atan2(dy, dx)  # 计算弧度
        degree = math.degrees(angle)  # 转换为角度
        return degree if degree >= 0 else degree + 360

    def mousePressEvent(self, event):
        """鼠标按下事件，记录当前鼠标位置用于平移"""
        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        """鼠标移动事件，更新当前激活的灯"""
        if self.last_pos:
            delta = event.pos() - self.last_pos
            self.offset += delta  # 更新偏移量
            self.last_pos = event.pos()  # 更新当前鼠标位置

        # 计算鼠标与原点的夹角
        angle = self.calculate_angle(event.pos())
        self.active_led_id = self.track.find_nearest_led(angle)
        self.update()  # 触发重绘

    def mouseReleaseEvent(self, event):
        """鼠标释放事件，重置鼠标拖动状态"""
        self.last_pos = None

    def wheelEvent(self, event):
        """鼠标滚轮事件，实现画面缩放"""
        angle_delta = event.angleDelta().y()  # 获取滚轮的增量

        if angle_delta > 0:
            self.scale_factor *= 1.1  # 放大
        else:
            self.scale_factor /= 1.1  # 缩小

        self.update()  # 更新界面

    def paintEvent(self, event):
        """绘制轨迹和灯"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算绘制的偏移位置
        painter.translate(self.offset)

        # 绘制坐标轴
        pen = QPen(Qt.gray, 1, Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(int(self.origin.x()), 0, int(self.origin.x()), self.height())  # Y轴
        painter.drawLine(0, int(self.origin.y()), self.width(), int(self.origin.y()))  # X轴

        # 绘制轨迹
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        for i in range(len(self.track.points) - 1):
            start_point = QPointF(self.track.points[i][0] * self.scale_factor, 
                                self.track.points[i][1] * self.scale_factor)
            end_point = QPointF(self.track.points[i + 1][0] * self.scale_factor, 
                                self.track.points[i + 1][1] * self.scale_factor)
            painter.drawLine(start_point, end_point)

        # 绘制灯
        for i, (x, y, _) in enumerate(self.track.lights):
            color = QColor(255, 0, 0) if i == self.active_led_id else QColor(200, 200, 200)
            painter.setBrush(color)
            painter.drawEllipse(QPointF(x * self.scale_factor, y * self.scale_factor).toPoint(), 5, 5)  # 绘制灯的小圆点

        # 绘制原点
        painter.setBrush(QColor(0, 255, 0))  # 原点为绿色
        painter.drawEllipse(self.origin, 5, 5)  # 绘制原点的小圆点

        # 绘制鼠标与原点的连线
        if self.active_led_id != -1:
            mouse_pos = self.mapFromGlobal(self.cursor().pos())
            painter.setPen(QPen(Qt.blue, 2, Qt.DashLine))
            painter.drawLine(self.origin, mouse_pos)  # 绘制连线

        painter.end()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 定义不规则轨迹的点 (这些点定义了一个不规则的轨迹)
    points = [(125, 250), (125, -250), (-125, -250), (-125, 250),(125, 250)]

    # 创建并显示窗口
    window = LightingApp(points)
    window.show()
    sys.exit(app.exec_())
