from PyQt5.QtWidgets import QGraphicsView, QLabel, QVBoxLayout
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF, QPoint

from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPolygonF, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from fence_tool import FenceTool


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

        self.fence_mode_active = False
        self.highlighted = True

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
        self.add_polygons()
        self.add_circles()
        # self.add_concentric_circles()
        # 添加一个绿色圆环，宽度为20
        # self.add_thick_circle(QPointF(0, 0), outer_radius=100, inner_radius=10, color=Qt.red)
        # 添加一个宽度为20的圆环，内圈填充为红色
        # self.add_thick_circle(QPointF(0, 0), outer_radius=1000, inner_radius=100, outer_color=Qt.green, inner_color=Qt.red)
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
                    self.fence_tool.draw_fences()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        """处理鼠标移动事件"""
        if self.fence_mode_active:
            # 获取鼠标当前位置并映射到场景坐标系
            pos = self.mapToScene(event.pos())
            # print(self.mapToScene(event.pos()))

            self.fence_tool.update_temp_line(pos)  # 更新临时线
            self.fence_tool.show_coordinates(pos)  # 显示坐标

    def add_polygons(self):
        """添加多个多边形区域"""
        polygons = [
            #             [QPointF(-100, 100), QPointF(-100, 0),
            #              QPointF(0, 0), QPointF(0, 100)],
            # # y+100
            #             [QPointF(-100, 100+100), QPointF(-100, 0+100),
            #              QPointF(0, 0+100), QPointF(0, 100+100)],
            # # x-100
            #              [QPointF(-100+100, 100), QPointF(-100+100, 0),
            #              QPointF(0+100, 0), QPointF(0+100, 100)],
            # # x-100  y+100
            #              [QPointF(-100+100, 100+100), QPointF(-100+100, 0+100),
            #              QPointF(0+100, 0+100), QPointF(0+100, 100+100)],
            [QPointF(-100, 220), QPointF(-100, -60),
             QPointF(100, -60), QPointF(100, 220)],

            [QPointF(-100, 340), QPointF(-100, -230),
             QPointF(-500, -230), QPointF(-500, 340)],

            [QPointF(100, 340), QPointF(100, -230),
             QPointF(500, -230), QPointF(500, 340)],

            [QPointF(300, 340), QPointF(300, 530),
             QPointF(-300, 530), QPointF(-300, 340)],

        ]

        for points in polygons:
            polygon = QPolygonF(points)
            polygon_item = QGraphicsPolygonItem(polygon)
            polygon_item.setPen(QPen(Qt.transparent, 2))
            polygon_item.setBrush(QBrush(Qt.transparent))
            self.scene().addItem(polygon_item)
            self.polygon_fences.append(polygon_item)

            # 画多边形顶点
            for point in points:
                self.add_fence_point(point)

    def add_fence_point(self, point):
        """在给定位置添加围栏的顶点"""
        ellipse = QGraphicsEllipseItem(point.x() - 5, point.y() - 5, 10, 10)
        ellipse.setPen(QPen(Qt.red))
        ellipse.setBrush(QBrush(Qt.red))
        self.scene().addItem(ellipse)

    def add_concentric_circles(self):
        """添加同心圆区域"""
        center = QPointF(0, 0)
        radii = [500, 300, 200]  # 定义同心圆的半径，按照半径从大到小排列
        real_r = [600, 400, 200]

        # 根据不同的半径创建同心圆
        for index, radius in enumerate(radii):
            # 创建圆
            circle_item = QGraphicsEllipseItem(
                center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)

            if index != len(radii)-1:
                circle_item.setPen(QPen(Qt.transparent, 200))
                circle_item.setBrush(QBrush(Qt.transparent))
            else:
                circle_item.setPen(QPen(Qt.transparent, 1))
                circle_item.setBrush(QBrush(Qt.transparent))
                # circle_item.setBrush(QBrush(Qt.green))
            # 将圆加入到场景中
            self.scene().addItem(circle_item)
            self.concentric_circles.append((circle_item, center, radius))

    def add_thick_circle(self, center, outer_radius, inner_radius, outer_color=Qt.green, inner_color=Qt.transparent):
        """添加具有特定宽度和颜色的圆环"""
        # 绘制外圆
        outer_circle_item = QGraphicsEllipseItem(center.x(
        ) - outer_radius, center.y() - outer_radius, 2 * outer_radius, 2 * outer_radius)
        outer_circle_item.setPen(QPen(outer_color, 2))  # 设置边框颜色和宽度
        outer_circle_item.setBrush(QBrush(inner_color))  # 设置内圈填充颜色
        self.scene().addItem(outer_circle_item)

        # 绘制内圆
        inner_circle_item = QGraphicsEllipseItem(center.x(
        ) - inner_radius, center.y() - inner_radius, 2 * inner_radius, 2 * inner_radius)
        inner_circle_item.setPen(QPen(Qt.transparent))  # 透明背景
        inner_circle_item.setBrush(QBrush(Qt.transparent))  # 透明背景
        self.scene().addItem(inner_circle_item)

        # 将圆环信息存储
        self.concentric_circles.append(
            (outer_circle_item, center, outer_radius))

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
        center = QPointF(0, 0)

        #  [200, 0, 200]

        # radius = 500
        # circle_item = QGraphicsEllipseItem(
        #     center.x() - radius, center.y() - radius, 2 * radius, 2 * radius)
        # circle_item.setPen(QPen(Qt.transparent))
        # circle_item.setBrush(QBrush(Qt.transparent))
        # self.scene().addItem(circle_item)
        # self.circle_fences.append((circle_item, center, 0, 500))

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
                # print(f"Key: {key}, Value: {value}")
                path_key = key
                if key not in self.lines:
                    self.lines[key] = {}
                    self.lines[key]['points'] = []
                    self.lines[key]['last_position'] = None  # 上一个点的位置
                    self.lines[key]['items'] = []  # 钥匙标志对象
                    self.lines[key]['item'] = None

                # self.lines[key]['points'].append((value['x'], value['y']))
                # self.lines[key]['last_position']=(value['x'], value['y'])
                x = value['x']
                y = value['y']
                new_position = QPointF(x, y)
                last_position = self.lines[key]['last_position']
                self.lines[key]['points'].append(new_position)
        except Exception as e:
            print(e)
            return
            # pass


        # self.lines[{path_key}]['path'].append((value['x'], value['y']))
        # print(self.lines[path_key])
        """更新钥匙位置并检查是否进入多边形或圆形区域"""

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
            line_item.setPen(QPen(Qt.red, 10))  # 设置线段颜色和宽度
            self.scene().addItem(line_item)
            self.lines[key]['items'].append(line_item)

            # 检查列表长度，超过50时删除第一个
            # if len(self.lines[key]['items']) > 50:
            #     first_line = self.lines[key]['items'].pop(0)
            #     self.scene().removeItem(first_line)
            #     first_line = self.lines[key]['items'].pop(0)
            #     self.scene().removeItem(first_line)

        # 移动钥匙
        if self.lines[key]['item'] is None:
            self.lines[key]['item'] = self.scene().addRect(
                x - 15, y - 15, 30, 30, QPen(Qt.red), QBrush(Qt.red))
        else:
            self.lines[key]['item'].setRect(x - 25, y - 25, 50, 50)

        # 检查钥匙是否进入多边形区域
        for polygon_item in self.polygon_fences:
            if polygon_item.polygon().containsPoint(new_position, Qt.OddEvenFill):
                if self.last_fence == polygon_item:
                    self.fence_cont += 1
                else:
                    self.last_fence = polygon_item

                if self.fence_cont >= 25:
                    self.fence_cont = 0
                    self.highlight_fence(polygon_item, True)  # 高亮多边形
                    for circle_item, _, min, max in self.circle_fences:

                        self.highlighted = True
                        if min == 0:
                            circle_item.setBrush(QBrush(Qt.transparent))
                        else:
                            circle_item.setPen(QPen(Qt.transparent))
            else:
                self.highlight_fence(polygon_item, False)  # 恢复透明
                self.highlighted = False

        # # # 检查钥匙是否进入圆形区域
        # for circle_item, center, radius in self.circle_fences:
        #     if (new_position - center).manhattanLength() <= radius:
        #         self.highlight_fence(circle_item, True)  # 高亮圆形
        #     else:
        #         self.highlight_fence(circle_item, False)  # 恢复透明

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
        center = QPoint(0, 0)  # 所有同心圆的中心相同
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
                    pass
                else:
                    circle_item.setPen(QPen(self.color_1, (max-min)))
                    pass
            else:
                if min == 0:
                    circle_item.setBrush(QBrush(Qt.transparent))
                    pass
                else:
                    circle_item.setPen(QPen(Qt.transparent))
                    pass
                pass

    def highlight_fence(self, fence_item, highlight):
        """高亮或取消高亮围栏区域"""
        if highlight:
            fence_item.setBrush(QBrush(QColor(255, 100, 255, 200)))  # 高亮为黄色
        else:
            fence_item.setBrush(QBrush(Qt.transparent))  # 恢复透明

    def highlight_ring(self, inner_circle_item, outer_circle_item, highlight):
        """
        高亮两个同心圆之间的圆环区域，或单独高亮最小圆或最大圆外区域
        inner_circle_item: 内圈圆 (如果高亮最小圆的内部，该值为 None)
        outer_circle_item: 外圈圆 (如果高亮最大圆外区域，该值为 None)
        highlight: 是否高亮
        """
        if inner_circle_item is None and outer_circle_item is None:
            return  # 如果两个都为空，没有可高亮的内容

        if inner_circle_item is None:  # 最小圆的内部区域
            if highlight:
                outer_circle_item.setBrush(
                    QBrush(QColor(255, 255, 0, 100)))  # 黄色半透明高亮
            else:
                outer_circle_item.setBrush(QBrush(Qt.NoBrush))  # 移除高亮
        elif outer_circle_item is None:  # 最大圆外的区域
            if highlight:
                inner_circle_item.setBrush(
                    QBrush(QColor(255, 0, 0, 100)))  # 红色半透明高亮
            else:
                inner_circle_item.setBrush(QBrush(Qt.NoBrush))  # 移除高亮
        else:  # 两个圆之间的圆环区域
            if highlight:
                max_circle_item, _, _ = self.concentric_circles[-1]
                max_circle_item.setBrush(QBrush(Qt.NoBrush))
                # 高亮两个圆之间的区域
                outer_circle_item.setBrush(
                    QBrush(QColor(0, 255, 0, 100)))  # 绿色半透明高亮
                inner_circle_item.setBrush(
                    QBrush(QColor(255, 0, 0, 100)))  # 移除高亮
                # inner_circle_item.setBrush(QBrush(QColor(0, 255, 0, 100)))  # 绿色半透明高亮
            else:
                pass
                inner_circle_item.setBrush(QBrush(Qt.NoBrush))  # 移除内圈高亮
                # outer_circle_item.setBrush(QBrush(Qt.NoBrush))  # 移除外圈高亮
                outer_circle_item.setBrush(QBrush(QColor(0, 255, 0, 100)))

    def drawForeground(self, painter, rect):
        """绘制无限延伸的X和Y坐标轴及刻度"""
        painter.save()
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        # painter.scale(1, -1)  # 仅翻转 Y 轴

        # 获取当前场景的可见区域
        view_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        # 获取当前缩放因子
        scale_x = self.transform().m11()  # x轴缩放因子
        scale_y = self.transform().m22()  # y轴缩放因子

        # 设置刻度间隔
        tick_interval = 100 * max(abs(scale_x), abs(scale_y))  # 根据缩放因子调整刻度间隔

        # 绘制X轴和刻度
        x_start = int(view_rect.left())
        x_end = int(view_rect.right())
        painter.drawLine(QPoint(x_start, 0), QPoint(x_end, 0))
        x = x_start - (x_start % tick_interval)
        while x < x_end:
            x_int = int(x)
            painter.drawLine(QPoint(x_int, -5), QPoint(x_int, 5))
            painter.drawText(x_int + 5, 15, str(x_int))
            x += tick_interval

        # 绘制Y轴和刻度
        y_start = int(view_rect.top())
        y_end = int(view_rect.bottom())
        painter.drawLine(QPoint(0, y_start), QPoint(0, y_end))
        y = y_start - (y_start % tick_interval)
        while y < y_end:
            y_int = int(y)
            painter.drawLine(QPoint(-5, y_int), QPoint(5, y_int))
            painter.drawText(15, y_int + 15, str(-y_int))
            y += tick_interval

        painter.restore()

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

    # def set_key_position(self, x, y):
        # """更新钥匙的位置并绘制轨迹"""
        # new_position = QPointF(x, y)

        # if last_position:
        #     pen = QPen(Qt.red, 2)
        #     self.scene().addLine(last_position.x(), last_position.y(), new_position.x(), new_position.y(), pen)

        # if self.key_item is None:
        #     self.key_item = self.scene().addEllipse(x - 5, y - 5, 10, 10, QPen(Qt.red), QBrush(Qt.red))
        # else:
        #     self.key_item.setRect(x - 5, y - 5, 10, 10)

        # last_position = new_position

        # # 更新钥匙的实时坐标显示
        # self.coord_label.setText(f"X: {x:.2f}, Y: {-y:.2f}")

        # # 确保钥匙在可见范围内
        # self.ensureVisible(self.key_item, 50, 50)
