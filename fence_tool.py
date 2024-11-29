from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsTextItem, QGraphicsPolygonItem
from shapely.geometry import Polygon
from PyQt5.QtGui import QPolygonF
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QInputDialog, QDialog

from datetime import datetime

from PyQt5.QtCore import Qt
import os
import json


class FenceTool:
    def __init__(self, scene):
        self.scene = scene
        self.fences = []  # 存储多个围栏
        self.points = []  # 当前围栏的点
        # 是否开启临时线
        self.is_temp_line = True

        # 点与鼠标位置的临时连接线
        self.temp_line = None
        # 第一个点与鼠标位置的临时连接线
        self.start_temp_line = None
        self.coord_label = None

        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.fence_path = os.path.join(
            self.current_path, "config", "fence.json")

        # self.highlight_fence_by_name('2024-11-28_1')

        # 加载已有的围栏数据
        self.load_fences_from_file()

    def save_fences_to_file(self):
        """将所有围栏数据保存到 JSON 文件"""
        # 将围栏的点转换成适合 JSON 存储的格式
        fences_data = []
        for name, points in self.fences:
            # 将每个点转换为字典格式
            points_data = [{"x": point.x(), "y": point.y()}
                           for point in points]
            fences_data.append({"name": name, "points": points_data})

        # 将数据写入 JSON 文件
        with open(self.fence_path, 'w') as file:
            json.dump(fences_data, file, indent=4)

    def load_fences_from_file(self):
        """从 JSON 文件加载围栏数据"""
        try:
            # 尝试读取文件
            with open(self.fence_path, 'r') as file:
                # 检查文件是否为空
                file_content = file.read().strip()
                if not file_content:
                    print("文件为空，未加载围栏数据。")
                    return []  # 返回空的围栏列表
                # 文件不为空，加载 JSON 数据
                fences_data = json.loads(file_content)
            # 清空当前的围栏数据
            self.fences = []
            # 遍历文件中的围栏数据
            for fence_data in fences_data:
                name = fence_data["name"]
                points = [QPointF(point["x"], point["y"])
                          for point in fence_data["points"]]
                self.fences.append((name, points))
        except FileNotFoundError:
            print(f"文件 {self.fence_path} 未找到，加载失败。")
            return []  # 如果文件不存在，返回空的围栏列表
        except json.JSONDecodeError:
            print(f"文件 {self.fence_path} 内容格式错误，加载失败。")
            return []  # 如果 JSON 格式错误，返回空的围栏列表

    def start(self):
        """开始电子围栏添加，重置已有的点和临时线"""
        self.points = []
        if self.temp_line:
            self.scene.removeItem(self.temp_line)
        self.temp_line = None

    def add_point(self, point):
        """添加一个点到围栏"""
        self.points.append(point)
        self.draw_fence()
        if len(self.points) >= 3:
            self.check_enclosure()

    def check_enclosure(self):
        """检查当前点是否围成一个围栏"""
        polygon = Polygon([(p.x(), p.y()) for p in self.points])
        if polygon.is_valid and polygon.area > 0:
            print("围栏已形成！")

    def draw_fence(self):
        """将点之间的连线绘制成围栏"""
        if len(self.points) > 1:
            for i in range(1, len(self.points)):
                line = self.scene.addLine(self.points[i - 1].x(), self.points[i - 1].y(),
                                          self.points[i].x(), self.points[i].y(), QPen(Qt.blue, 2))

    def undo(self):
        """撤销上一个点"""
        if self.points:
            self.points.pop()  # 移除最后一个点

    def get_fence_name(self, parent):
        """弹出对话框获取电子围栏名称"""
        base_name = datetime.now().strftime("%Y-%m-%d")  # 当前日期
        index = len(self.fences) + 1  # 序号累加
        default_name = f"{base_name}_{index}"

        dialog = QInputDialog(parent)
        dialog.setWindowTitle("命名电子围栏")
        dialog.setLabelText("请输入电子围栏名称:")
        dialog.setTextValue(default_name)
        dialog.setFixedSize(400, 100)  # 设置输入框的固定大小

        if dialog.exec_() == QDialog.Accepted:
            name = dialog.textValue()
            return name

        return default_name  # 如果没有输入，则使用默认名称

    def finish_fence(self, parent):
        """完成当前围栏并保存"""
        if len(self.points) >= 3:
            name = self.get_fence_name(parent)
            self.fences.append((name, self.points))
            # 绘制起始点和结束点的连线
            start_point = self.points[0]  # 获取起始点
            end_point = self.points[-1]    # 获取结束点
            # line = QLineF(start_point, end_point)  # 创建连线

            line = self.scene.addLine(start_point.x(), start_point.y(
            ), end_point.x(), end_point.y(), QPen(Qt.blue, 2))

            # self.scene.addLine(line, QPen(Qt.black))  # 添加到场景中，使用黑色线条
            self.points = []  # 清空当前围栏
            if self.start_temp_line:
                self.scene.removeItem(self.start_temp_line)
            if self.temp_line:
                self.scene.removeItem(self.temp_line)
            self.save_fences_to_file()

    def draw_fence_polygon(self, points, color=Qt.blue, fill_color=Qt.transparent, border_width=2):
        """绘制围栏的多边形区域"""
        polygon = QPolygonF()  # 创建多边形

        # 将围栏的点添加到多边形中
        for point in points:
            polygon.append(QPointF(point.x(), point.y()))

        # 如果 border_width 为 0，则不绘制边框
        if border_width > 0:
            polygon_item = self.scene.addPolygon(
                polygon, QPen(color, border_width), QBrush(fill_color))
        else:
            polygon_item = self.scene.addPolygon(polygon, QPen(
                Qt.transparent), QBrush(fill_color))  # 不显示边框，透明线条

        return polygon_item

    def highlight_fence_by_name(self, name):
        """通过围栏名称高亮显示围栏"""
        # 清除场景中的所有已绘制的围栏
        self.clear_all_fences()

        # 遍历所有围栏，找到匹配的名称并高亮
        for fence_name, points in self.fences:
            if fence_name == name:
                # 高亮围栏，只显示填充颜色，没有边框
                self.draw_fence_polygon(points, color=Qt.transparent, fill_color=QColor(
                    255, 0, 0, 150), border_width=0)
            else:
                # 普通围栏，使用透明边框并无填充
                self.draw_fence_polygon(
                    points, color=Qt.transparent, fill_color=Qt.transparent, border_width=0)

    def is_point_in_polygon(self, point, polygon_points):
        """判断点是否在围栏（多边形）内"""
        polygon = QPolygonF()

        # 将围栏的点添加到多边形中
        for pt in polygon_points:
            polygon.append(QPointF(pt.x(), pt.y()))

        # 使用QPolygonF的containsPoint方法判断点是否在多边形内
        # Qt.OddEvenFill用于判断点在多边形内
        return polygon.containsPoint(point, Qt.OddEvenFill)

    def highlight_fence_by_point(self, point):
        """通过坐标点判断并高亮该点所在的围栏"""
        # 清除场景中的所有已绘制的围栏
        # self.clear_all_fences()
        fences = []

        # 遍历所有围栏，找到包含点的围栏并高亮
        for fence_name, points in self.fences:
            temp_item = None
            # 判断点是否在围栏（多边形）内
            if self.is_point_in_polygon(point, points):
                # 高亮围栏
                temp_item = self.draw_fence_polygon(points, color=Qt.red, fill_color=QColor(
                    255, 0, 0, 50), border_width=0)
            # else:
            #     # 普通围栏，不高亮
            #     temp_item = self.draw_fence_polygon(
            #         points, color=Qt.blue, fill_color=Qt.transparent, border_width=0)
            fences.append(temp_item)
        return fences

    def clear_all_fences(self):
        """清除所有已绘制的围栏线条和区域"""
        for item in self.scene.items():
            if isinstance(item, QGraphicsPolygonItem):
                self.scene.removeItem(item)  # 移除围栏的多边形项
            # elif isinstance(item, QGraphicsLineItem):
            #     self.scene.removeItem(item)  # 移除围栏的线条项

    def update_temp_line(self, current_pos):
        """绘制临时线，从上一个点到当前鼠标位置"""
        if self.is_temp_line == False:
            return
        if len(self.points) > 0:
            last_point = self.points[-1]

            if self.temp_line:
                self.scene.removeItem(self.temp_line)

            # 绘制从上一个点到当前鼠标位置的线
            self.temp_line = self.scene.addLine(last_point.x(), last_point.y(),
                                                current_pos.x(), current_pos.y(), QPen(Qt.gray, 1))

            # 如果超过两个点，绘制从第一个点到当前鼠标位置的线
            if len(self.points) > 2:
                # 删除上一条临时线
                if self.start_temp_line:
                    self.scene.removeItem(self.start_temp_line)

                first_point = self.points[0]
                self.start_temp_line = self.scene.addLine(first_point.x(), first_point.y(),
                                                          current_pos.x(), current_pos.y(), QPen(Qt.gray, 1))

    def show_coordinates(self, current_pos):
        """在鼠标附近显示坐标"""
        if self.coord_label:
            self.scene.removeItem(self.coord_label)

        self.coord_label = QGraphicsTextItem(
            f"({int(current_pos.x())}, {int(current_pos.y())})")
        self.coord_label.setPos(current_pos.x() + 10, current_pos.y() - 10)
        self.scene.addItem(self.coord_label)
