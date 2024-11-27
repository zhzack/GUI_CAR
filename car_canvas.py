import random
from PyQt5.QtWidgets import QGraphicsView, QLabel
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF, QPoint

from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPolygonF, QPen, QBrush, QColor, QPixmap
from PyQt5.QtCore import Qt, QRect

from fence_tool import FenceTool
import os

lineLen = 10


class CarCanvas(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(CarCanvas, self).__init__(scene, parent)
        # print(f"父类类型: {type(parent)}")  # 打印父类的类型
        self.parent = parent
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.queue=None
        self.fence_mode_active = False
        self.mouse_move_active = True
        self.highlighted = False

        self.fence_tool = FenceTool(scene)

        self.color_0 = QColor(255, 255, 0, 50)
        self.color_1 = QColor(255, 255, 0, 100)

        self.last_fence = None  # 钥匙上一个所在的区域
        self.fence_cont = 0
        self.zoom_factor = 1  # 缩放系数

        # 允许显示超出场景范围的内容
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setSceneRect(-2000, -2000, 4000, 4000)  # 调整场景边界大小

        self.lines = {}  # 存储线段对象，不同输入的轨迹保存

        # 存储多个多边形和圆形区域
        self.polygon_fences = []
        self.circle_fences = []
        self.concentric_circles = []
        self.key_item = None

        # 添加多个多边形和圆形区域
        self.add_circles()

        # 创建浮动展示台
        self.float_widget = QLabel("", self)

        self.float_widget.setStyleSheet(
            "QLabel { background-color : rgba(255, 0, 255, 38); padding: 10px; font-size: 18px; }")
        self.float_widget.setFixedSize(500, 150)  # 设置固定大小，确保有高度

        self.coord_label = self.float_widget

        # 更新浮动展示台的位置
        self.update_float_position()

    def resizeEvent(self, event):
        self.update_float_position()

    def update_float_position(self):
        # 计算浮动展示台的位置，固定在右上角
        x = self.width() - self.float_widget.width() - 15  # 右边距10
        y = 0  # 上边距10
        self.float_widget.setGeometry(
            QRect(x, y, self.float_widget.width(), self.float_widget.height()))

    def set_fence_mode(self, active):
        """启用或禁用电子围栏添加模式"""
        self.fence_mode_active = active

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        """处理鼠标点击事件"""
        if self.fence_mode_active:
            # 判断是否是右键点击
            if event.button() == Qt.RightButton:
                # 获取鼠标点击的位置并映射到场景坐标系
                pos = self.mapToScene(event.pos())
                # 发射鼠标点击信号
                self.fence_tool.add_point(pos)

    def keyPressEvent(self, event):
        """处理键盘按键事件"""
        if self.fence_mode_active:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:  # 检查是否按下 Ctrl + 回车
                if self.fence_mode_active:
                    # 完成围栏的操作
                    self.fence_tool.finish_fence(self.parent)
                    # self.fence_tool.draw_fences()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        """处理鼠标移动事件"""
        if self.fence_mode_active:
            # 获取鼠标当前位置并映射到场景坐标系
            pos = self.mapToScene(event.pos())
            # print(self.mapToScene(event.pos()))

            self.fence_tool.update_temp_line(pos)  # 更新临时线
            self.fence_tool.show_coordinates(pos)  # 显示坐标
        if self.mouse_move_active:
            pos = self.mapToScene(event.pos())
            parsed_data={}
            parsed_data['鼠标'] = {'x': pos.x(), 'y': pos.y()}
            # print(parsed_data)
            self.queue.put([parsed_data])

    def add_circles(self):
        """添加多个圆形区域"""
        # circles = [
        #     [300, 200, 400],  # 圆心坐标和半径
        #     [500, 400, 600],
        #     [700, 600, 800],
        #     [900, 800, 1000]
        # ]
        circles = [
            # 圆心坐标和半径
            [650, 500, 800],
            [1500, 800, 1500]
        ]

        # for i in range(0, len(circles)):
        center = QPointF(90, -220)

        for circle in circles:
            radius = (circle[2]+circle[1])/2
            circle_item = QGraphicsEllipseItem(
                center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)
            circle_item.setPen(QPen(self.color_1, (circle[2]-circle[1])))
            circle_item.setBrush(QBrush(Qt.transparent))

            self.scene().addItem(circle_item)
            self.circle_fences.append(
                (circle_item, center, circle[1], circle[2]))

    def set_key_position(self, object):
        path_key = ''
        x = 0
        y = 0
        try:
            for key, value in object.items():
                print(f"Key: {key}, Value: {value}")
                path_key = key
                if key not in self.lines:
                    self.lines[key] = {}
                    self.lines[key]['points'] = []
                    self.lines[key]['last_position'] = None  # 上一个点的位置
                    self.lines[key]['items'] = []  # 钥匙标志对象
                    self.lines[key]['item'] = None

                    # 创建随机颜色
                    self.lines[key]['color'] = QColor(random.randint(
                        0, 255), random.randint(0, 255), random.randint(0, 255))

                # self.lines[key]['points'].append((value['x'], value['y']))
                # self.lines[key]['last_position']=(value['x'], value['y'])
                x = value['x']
                y = value['y']
                new_position = QPointF(x, y)
                self.fence_tool.highlight_fence_by_point(new_position)
                last_position = self.lines[key]['last_position']
                self.lines[key]['points'].append(new_position)
        except Exception as e:
            print(e)
            return
            # pass

        # self.lines[{path_key}]['path'].append((value['x'], value['y']))
        # print(self.lines[path_key])
        """更新钥匙位置并检查是否进入多边形或圆形区域"""
        # for key in self.lines:
        #     print(key)
        self.coord_label.setText(
            f"""
            <div style='font-size: 28px;'>
                <span style='color: green;'>真实坐标点: ({x:.2f}, {-y:.2f})</span><br>
                <span style='color: red;'>UWB钥匙坐标点: ({x:.2f}, {-y:.2f})</span><br>
                <span style='color: purple;'>蓝牙定位区域</span><br>
            </div>
            """
        )
        if last_position:

            line_item = QGraphicsLineItem(last_position.x(), last_position.y(),
                                          new_position.x(), new_position.y())
            line_item.setPen(QPen(self.lines[key]['color'], 5))  # 设置线段颜色和宽度
            self.scene().addItem(line_item)
            self.lines[key]['items'].append(line_item)

            # 检查列表长度，超过50时删除第一个
            if len(self.lines[key]['items']) > lineLen:
                first_line = self.lines[key]['items'].pop(0)
                self.scene().removeItem(first_line)
                first_line = self.lines[key]['items'].pop(0)
                self.scene().removeItem(first_line)

        # 移动钥匙
        if self.lines[key]['item'] is None:
            self.lines[key]['item'] = self.scene().addRect(
                x - 7.5, y - 7.5, 15, 15, QPen(self.lines[key]['color']), QBrush(self.lines[key]['color']))
        else:
            self.lines[key]['item'].setRect(x - 7.5, y - 7.5, 15, 15)

        # 检查钥匙是否进入同心圆的圆环区域
        self.check_concentric_circles(new_position)

        self.lines[key]['last_position'] = new_position

        # print(int(self.width()/2),int(self.height()/2))
        # 确保钥匙在可见范围内
        # self.ensureVisible(self.key_item, int(
        #     self.width()/2)-40, int(self.height()/2)-40)

    def check_concentric_circles(self, position):
        if self.highlighted:
            return
        """检查钥匙是否在同心圆的圆环或范围之外"""
        # 计算钥匙到圆心的距离
        center = QPoint(90, -220)  # 所有同心圆的中心相同
        distance_to_center = ((position.x() - center.x())
                              ** 2 + (position.y() - center.y())**2)**0.5

        # 初始化一个标志来追踪是否已高亮圆环
        # highlighted = False
        for circle_item, _, min, max in self.circle_fences:

            if min < distance_to_center < max:
                # highlighted = True
                if min == 0:
                    # print(1)
                    circle_item.setBrush(QBrush(self.color_1))  # 高亮为黄色
                    # circle_item.setPen(QPen(Qt.green,200))
                else:
                    circle_item.setPen(QPen(self.color_1, (max-min)))
            else:
                if min == 0:
                    circle_item.setBrush(QBrush(Qt.transparent))
                else:
                    circle_item.setPen(QPen(Qt.transparent))

    def wheelEvent(self, event):
        """鼠标滚轮缩放"""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
            self.zoom_factor *= zoom_in_factor
        else:
            self.scale(zoom_out_factor, zoom_out_factor)
            self.zoom_factor *= zoom_out_factor
