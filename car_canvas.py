import random
from PyQt5.QtWidgets import QGraphicsView, QLabel
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF, QPoint

from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QRect

from fence_tool import FenceTool
from float_list import CustomFloatList

lineLen = 10


class CarCanvas(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(CarCanvas, self).__init__(scene, parent)
        self.parent = parent
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.queue = None
        self.fence_mode_active = False
        self.mouse_move_active = True
        self.highlighted = False

        self.fence_tool = parent.fence_tool

        self.last_fence = None  # 钥匙上一个所在的区域
        self.fence_cont = 0
        self.zoom_factor = 1  # 缩放系数

        # 允许显示超出场景范围的内容
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setSceneRect(-2000, -2000, 4000, 4000)  # 调整场景边界大小

        self.lines = {}  # 存储线段对象，不同输入的轨迹保存

        self.center = QPointF(90, -220)

        # 存储多个多边形和圆形区域
        self.circles = [
            # 圆心坐标和半径
            [500, 800],
            [800, 1500]
        ]
        self.polygon_fences = []
        self.concentric_circles = []
        self.key_item = None

        # 初始化浮动窗口
        self.floatList = CustomFloatList(scene, self)  # 父对象为视图

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
            parsed_data = {}
            parsed_data['鼠标'] = {'x': pos.x(), 'y': pos.y()}
            # print(parsed_data)
            self.queue.put([parsed_data])

    def check_concentric_circles(self, position):
        # 计算钥匙到圆心的距离
        distance_to_center = ((position.x() - self.center.x())
                              ** 2 + (position.y() - self.center.y())**2)**0.5
        # 初始化一个标志来追踪是否已高亮圆环
        for min, max in self.circles:
            if min < distance_to_center < max:
                radius = (min+max)/2
                circle_item = QGraphicsEllipseItem(
                    self.center.x() - radius, self.center.y() - radius, 2 * radius, 2 * radius)
                circle_item.setPen(QPen(QColor(255, 0, 0, 60), (max-min)))
                circle_item.setBrush(QBrush(Qt.transparent))
                self.scene().addItem(circle_item)
                return circle_item

    def set_ble_area(self, object):
        temp_key_obj = {}
        ble1 = 0
        ble2 = 0
        for key, value in object.items():
            if key not in self.lines:
                temp_key_obj['fences'] = []
                # 创建随机颜色
                temp_key_obj['color'] = QColor(random.randint(
                    100, 255), random.randint(100, 255), random.randint(100, 255))
                temp_key_obj['list_text_item'] = None

                self.lines[key] = temp_key_obj
            else:
                temp_key_obj = self.lines[key]
            ble1 = value['x']
            ble2 = value['y']

        text = self.fence_tool.check_position(ble1)

        if temp_key_obj['list_text_item'] == None:
            temp_key_obj['list_text_item'] = self.floatList.add_item(
                text, temp_key_obj['color'])
        else:
            self.floatList.updateItemByIndex(
                temp_key_obj['list_text_item'], text)

    def set_key_position(self, object):
        path_key = ''
        x = 0
        y = 0
        try:
            for key, value in object.items():
                # print(f"Key: {key}, Value: {value}")
                temp_key_obj = {}
                if key not in self.lines:
                    temp_key_obj['points'] = []
                    temp_key_obj['last_position'] = None  # 上一个点的位置
                    temp_key_obj['items'] = []  # 钥匙标志对象
                    temp_key_obj['item'] = None
                    temp_key_obj['temp_line'] = None
                    temp_key_obj['fences'] = []
                    # 创建随机颜色
                    temp_key_obj['color'] = QColor(random.randint(
                        100, 255), random.randint(100, 255), random.randint(100, 255))
                    temp_key_obj['list_text_item'] = None

                    self.lines[key] = temp_key_obj
                else:
                    temp_key_obj = self.lines[key]

                x = value['x']
                y = value['y']
                new_position = QPointF(x, y)

                if key != 'BLE':
                    x1 = x
                    y1 = y
                    if key == '鼠标':
                        y1 = -y
                    text = f'{key}: x:{x1:.2f},y:{y1:.2f}'
                    if temp_key_obj['list_text_item'] == None:
                        temp_key_obj['list_text_item'] = self.floatList.add_item(
                            text, temp_key_obj['color'])
                    else:
                        self.floatList.updateItemByIndex(
                            temp_key_obj['list_text_item'], text)

                if temp_key_obj['temp_line']:
                    self.scene().removeItem(temp_key_obj['temp_line'])
                # 绘制从主驾车门到当前点位置的线
                temp_key_obj['temp_line'] = self.scene().addLine(0, -200,
                                                                 x, y, QPen(Qt.gray, 3))

                # 清除上一个点的高亮
                if temp_key_obj['fences'] != None:
                    for fence in temp_key_obj['fences']:
                        if fence is not None:
                            self.scene().removeItem(fence)
                temp_key_obj['fences'] = self.fence_tool.highlight_fence_by_point(
                    new_position)
                # 检查钥匙是否进入同心圆的圆环区域
                temp_key_obj['fences'].append(self.check_concentric_circles(
                    new_position))

                if temp_key_obj['last_position']:

                    line_item = QGraphicsLineItem(temp_key_obj['last_position'].x(), temp_key_obj['last_position'].y(),
                                                  new_position.x(), new_position.y())
                    line_item.setPen(
                        QPen(temp_key_obj['color'], 5))  # 设置线段颜色和宽度
                    self.scene().addItem(line_item)
                    temp_key_obj['items'].append(line_item)

                    # 检查列表长度，超过50时删除第一个
                    if len(temp_key_obj['items']) > lineLen:
                        first_line = temp_key_obj['items'].pop(0)
                        self.scene().removeItem(first_line)

                # 移动钥匙
                if temp_key_obj['item'] is None:
                    temp_key_obj['item'] = self.scene().addRect(
                        x - 7.5, y - 7.5, 15, 15, QPen(temp_key_obj['color']), QBrush(temp_key_obj['color']))
                else:
                    temp_key_obj['item'].setRect(x - 7.5, y - 7.5, 15, 15)

                temp_key_obj['last_position'] = new_position

                # print(int(self.width()/2),int(self.height()/2))
                # 确保钥匙在可见范围内
                # self.ensureVisible(self.key_item, int(
                #     self.width()/2)-40, int(self.height()/2)-40)

                # temp_key_obj['last_position'] = temp_key_obj['last_position']
                temp_key_obj['points'].append(new_position)
                self.lines[key] = temp_key_obj
        except Exception as e:
            print(e)
            return
            # pass

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
