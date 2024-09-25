from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen,QPainter
from PyQt5.QtWidgets import QGraphicsTextItem
from shapely.geometry import Polygon
from PyQt5.QtGui import QPainterPath
from PyQt5.QtGui import QPainterPath, QPen, QBrush,QColor
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtWidgets import QInputDialog, QDialog

from datetime import datetime

from PyQt5.QtCore import Qt


class FenceTool:
    def __init__(self, scene):
        self.scene = scene
        self.fences = []  # 存储多个围栏
        self.points = []  # 当前围栏的点
        # 是否开启临时线
        self.is_temp_line=True

        # 点与鼠标位置的临时连接线
        self.temp_line = None
        # 第一个点与鼠标位置的临时连接线
        self.start_temp_line=None
        self.coord_label = None

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
    
    def get_fence_name(self,parent):
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
            
    def finish_fence(self,parent):
        """完成当前围栏并保存"""
        if len(self.points) >= 3:
            name=self.get_fence_name(parent)
            self.fences.append((name,self.points))
            # 绘制起始点和结束点的连线
            start_point = self.points[0]  # 获取起始点
            end_point = self.points[-1]    # 获取结束点
            # line = QLineF(start_point, end_point)  # 创建连线

            line = self.scene.addLine(start_point.x(),start_point.y(),end_point.x(),end_point.y(), QPen(Qt.blue, 2))

            # self.scene.addLine(line, QPen(Qt.black))  # 添加到场景中，使用黑色线条
            self.points = []  # 清空当前围栏
            if self.start_temp_line:
                self.scene.removeItem(self.start_temp_line)
            if self.temp_line:
                self.scene.removeItem(self.temp_line)


        
            
    def draw_fences(self):
        """绘制所有围栏区域"""
        for _,fence in self.fences:
            print(fence)
            if len(fence) >= 3:
                # 将围栏的点转换为 QPointF
                polygon = [QPointF(p.x(), p.y()) for p in fence]
                # 在画布上绘制这个多边形
                self.highlight_area(polygon)


    def highlight_area(self, polygon):
        """高亮区域"""
        path = QPainterPath()

        # 确保传入的 polygon 是有效的 QPointF 列表
        if polygon and len(polygon) > 0:
            path.moveTo(polygon[0])  # 移动到第一个点
            for point in polygon[1:]:
                path.lineTo(point)  # 连接到后续的点

        # 绘制路径
        path_item = QGraphicsPathItem(path)
        path_item.setBrush(QBrush(QColor(255, 255, 0, 100)))  # 设置高亮颜色
        self.scene.addItem(path_item)  # 直接使用 self.scene 而不是 self.scene()




    def update_temp_line(self, current_pos):
        """绘制临时线，从上一个点到当前鼠标位置"""
        if self.is_temp_line==False:
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
                self.start_temp_line=self.scene.addLine(first_point.x(), first_point.y(), 
                                current_pos.x(), current_pos.y(), QPen(Qt.gray, 1))


    def show_coordinates(self, current_pos):
        """在鼠标附近显示坐标"""
        if self.coord_label:
            self.scene.removeItem(self.coord_label)
        
        self.coord_label = QGraphicsTextItem(f"({int(current_pos.x())}, {int(current_pos.y())})")
        self.coord_label.setPos(current_pos.x() + 10, current_pos.y() - 10)
        self.scene.addItem(self.coord_label)
