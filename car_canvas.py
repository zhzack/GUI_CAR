import random
from PyQt5.QtWidgets import QGraphicsView, QLabel, QVBoxLayout
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF, QPoint

from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtCore import QTimer, Qt

import math
import requests

# from lightCalculator import LightCalculator
import lightCalculator


from fence_tool import FenceTool
from float_list import CustomFloatList

# from serve.communication_interface import CommunicationInterface
from serve.SerialManager import SerialManager
from serve.TCPServerManager import TCPServer
from serve.ServoController import ServoController
from serve.ws2812 import Ws2812
from VectorDisplay import VectorDisplay
import tkinter as tk
from PyQt5.QtCore import QProcess
import time

lineLen = 10000


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
        self.data_queue = None
        self.fence_mode_active = False
        self.mouse_move_active = False
        # self.mouse_move_active = True
        self.highlighted = False

        self.fence_tool = parent.fence_tool

        self.manager = None
        self.ws2812 = None
        self.servo = None
        self.total_angle = 0
        self.previous_angle = 0
        self.last_send_angle = 0
        self.last_time = 0
        self.init_servo_ws2812()

        self.last_fence = None  # 钥匙上一个所在的区域
        self.fence_cont = 0
        self.zoom_factor = 1  # 缩放系数

        # 允许显示超出场景范围的内容
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        # self.setSceneRect(-6000, -6000, 6000, 6000)  # 调整场景边界大小

        self.lines = {}  # 存储线段对象，不同输入的轨迹保存

        # 存储多个多边形和圆形区域
        self.circles = [
            # 圆心坐标和半径
            # [500, 800],
            [800, 1500]
        ]
        self.center = QPointF(90, -220)

        self.polygon_fences = []
        self.concentric_circles = []
        self.key_item = None

        self.ble_fences = {}

        # self.lightCa = LightCalculator()

        # 初始化浮动窗口
        self.floatList = CustomFloatList(scene, "小车和UWB位置坐标", self)  # 父对象为视图
        self.floatListBLE = CustomFloatList(
            scene, "蓝牙定位结果（粉色范围）", self)  # 父对象为视图

    # def setup_layout(self, item, pos):
        """设置 CarCanvas 的布局，包括浮动窗口"""
        # 创建 QVBoxLayout 管理 CarCanvas 的控件
        self.layout = QVBoxLayout(self)  # 这里使用 CarCanvas 自己的布局

        # 将 CarCanvas 添加到布局
        self.layout.addWidget(self)  # 添加 CarCanvas 作为布局中的第一个控件

        # 将浮动窗口添加到布局并设置对齐方式
        # layout.addWidget(self.floatList)  # 将 floatList 添加到布局中
        # layout.setAlignment(self.floatList, Qt.AlignLeft | Qt.AlignTop)  #

        self.layout.addWidget(self.floatListBLE)  # 将 floatList 添加到布局中
        self.layout.setAlignment(self.floatListBLE, Qt.AlignRight |
                                 Qt.AlignTop)  # 将浮动窗口放置在右上角

        self.setLayout(self.layout)

        self.parent.setLayout(self.layout)

    def init_servo_ws2812(self):
        # 创建串口管理实例
        # self.manager = SerialManager(port_by_keyword='CH', baudrate=115200)
        # self.manager = TCPServer(host='172.20.10.2', port=80)
        self.manager = TCPServer(host='0.0.0.0', port=80)

        self.ws2812 = Ws2812(self.manager)
        self.ws2812.num_strips = 15
        # 创建舵机控制实例
        self.servo = ServoController(self.manager)
        servo_id = 0
        time_ms = 5
        angle = 0
        # pos = servo.get_position(servo_id)
        # print(pos)
        # self.servo.half_reset(0)
        # time.sleep(2)
        #  self.half_reset(0)

    def set_angle(self, angle):
        print(f"angle:{angle}")
        temp_angle = self.total_angle
        current_time = int(time.time() * 1000)
        if current_time-self.last_time < 500:
            # print("输出过快了")
            # return
            pass
        self.last_time = current_time

        servo_id = 0
        time_ms = 5
        previous_angle = self.previous_angle
        total_angle = self.total_angle

        current_angle = angle
        # 当前角度与前一个角度的差值
        if previous_angle == 0:
            total_angle = current_angle
        else:

            diff = current_angle - previous_angle

            # 如果差值大于 180，说明跨过 360°，需要调整
            if diff > 180:
                diff -= 360
            # 如果差值小于 -180，说明跨过 0°，需要调整
            elif diff < -180:
                diff += 360

            # 累加调整后的差值
            total_angle += diff

        self.total_angle = total_angle
        # 更新上一个角度值
        self.previous_angle = current_angle

        print(self.total_angle)
        if abs(self.last_send_angle-self.total_angle) > 5:
            # self.manager.send_data(f'#{int(self.total_angle)}!')
            self.last_send_angle = self.total_angle

        self.ws2812.set_led_angle(angle)
        # # time.sleep(0.01)
        # self.servo.set_angle(servo_id, angle, time_ms)
        # time.sleep(0.01)  # 延迟 1 秒
        # pos = servo.get_position(servo_id)
        # print(pos)

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
            parsed_data['鼠标'] = {
                'x': pos.x(), 'y': pos.y(), 'StopFlag': True}
            # print(parsed_data)
            self.queue.put([parsed_data])

    def check_concentric_circles(self, position, scene):
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
                scene.addItem(circle_item)
                return circle_item

    def addLabel(self, results_desc):
        # 创建 QLabel 控件
        temp_label_widget = QLabel(results_desc, self)

        # 设置标签文本样式（可选）
        temp_label_widget.setStyleSheet(
            "font-size: 88px; color: #fe5700; background-color: #01c8ac; padding: 15px;")

        # 设置标签的对齐方式（例如，居中）
        temp_label_widget.setAlignment(Qt.AlignCenter)

        # 将 floatList 添加到布局中
        self.layout.addWidget(temp_label_widget)
        self.layout.setAlignment(
            # 将浮动窗口放置在右上角
            temp_label_widget, Qt.AlignCenter | Qt.AlignTop)
        temp_label_widget.move(1000, 1000)
        # 创建一个定时器（QTimer）
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)  # 设置为单次触发
        self.timer.timeout.connect(
            lambda: self.delete_label(temp_label_widget))  # 传递标签作为参数
        self.timer.start(1000)  # 设置定时器在 500 毫秒后触发

        return

    def delete_label(self, label):
        """删除传入的标签并销毁"""
        label.deleteLater()  # 删除标签
        print("Label deleted!")

    def set_ble_area(self, object):
        temp_key_obj = {}
        ble = 0
        for key, value in object.items():
            if key not in self.ble_fences:
                temp_key_obj['fences'] = None
                temp_key_obj['cir_fences'] = None
                # 创建随机颜色
                # temp_key_obj['color'] = QColor(random.randint(
                #     100, 255), random.randint(100, 255), random.randint(100, 255))
                temp_key_obj['color'] = QColor(255, 0, 0)
                temp_key_obj['list_text_item'] = None
                temp_key_obj['label'] = None

                self.ble_fences[key] = temp_key_obj
            else:
                temp_key_obj = self.ble_fences[key]

            ble = value['x']

            results_desc, fences = self.fence_tool.check_position(ble)

            # 创建文字列表
            if temp_key_obj['list_text_item'] == None:
                self.floatListBLE.add_item('')

                temp_key_obj['list_text_item'] = self.floatListBLE.add_item(
                    results_desc, temp_key_obj['color'])
                temp_key_obj['label'] = self.addLabel(results_desc)

            else:
                if temp_key_obj['last_text'] != '' and temp_key_obj['last_text'] != results_desc:
                    self.floatListBLE.start_blink(
                        temp_key_obj['list_text_item'])
                    if temp_key_obj['label'] != None:
                        print(temp_key_obj['label'])
                        self.layout.removeWidget(temp_key_obj['label'])
                        temp_key_obj['label'] = None
                    temp_key_obj['label'] = self.addLabel(results_desc)

                self.floatListBLE.updateItemByIndex(
                    temp_key_obj['list_text_item'], f'蓝牙：{results_desc}')

            temp_key_obj['last_text'] = results_desc

            # # 清除蓝牙高亮
            if temp_key_obj['fences'] != None:
                self.fence_tool.scene.removeItem(temp_key_obj['fences'])
            if temp_key_obj['cir_fences'] != None:
                self.scene().removeItem(temp_key_obj['cir_fences'])

                temp_key_obj['cir_fences'] = None
            # 设置高亮
            for name in fences:
                if name != None:
                    temp_key_obj['fences'] = self.fence_tool.highlight_fence_by_name(
                        name)

                    if name == 0x2:
                        min = 800
                        max = 1500
                        radius = (min+max)/2
                        circle_item = QGraphicsEllipseItem(
                            self.center.x() - radius, self.center.y() - radius, 2 * radius, 2 * radius)
                        circle_item.setPen(
                            QPen(QColor(255, 0, 0, 60), (max-min)))
                        circle_item.setBrush(QBrush(Qt.transparent))
                        self.scene().addItem(circle_item)
                        temp_key_obj['cir_fences'] = circle_item
                        temp_key_obj['last_text'] = ''

            self.ble_fences[key] = temp_key_obj

    def calculate_angle(self, x2, y2):
        x1 = 90
        y1 = 210
        # 使用 atan2 计算角度，返回值是弧度
        angle_rad = math.atan2(y2 - y1, x2 - x1)
        print(f"{angle_rad}")
        # 将角度转换为度数
        angle_deg = math.degrees(angle_rad)
        print(f"{angle_deg}")
        if angle_deg < 0:
            angle_deg += 360

        return angle_deg
    def calculate_angle_1(self, x2, y2):
        x1 = 90
        y1 = 210
        # 使用 atan2 计算角度，返回值是弧度
        angle_rad = math.atan2(-(y2 - y1), -(x2 - x1))
        # print(f"{angle_rad}")
        # 将角度转换为度数
        angle_deg = math.degrees(angle_rad)
        # print(f"{angle_deg}")
        if angle_deg < 0:
            angle_deg += 360

        return angle_deg

    def set_key_position(self, object):
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
                    if key == 'UWB1':
                        temp_key_obj['color'] = QColor(0, 0, 255)
                    elif key == 'UWB2':
                        temp_key_obj['color'] = QColor(0, 255, 0)
                    else:
                        temp_key_obj['color'] = QColor(random.randint(
                            100, 255), random.randint(100, 255), random.randint(100, 255))

                    temp_key_obj['list_text_item'] = None

                    # temp_key_obj['app']=VectorDisplay()

                    # temp_key_obj['process'] = QProcess(self)  # 创建 QProcess 实例
                    # temp_key_obj['process'].start("python", ["VectorDisplay.py"])  # 启动 Tkinter 窗口

                    self.lines[key] = temp_key_obj
                else:
                    temp_key_obj = self.lines[key]

                x = value['x']
                y = value['y']
                StopFlag = value['StopFlag']

                # coord_str = f"{int(x)} {int(y)}\n"
                # self.lines[key]['process'].write(coord_str.encode())
                # self.lines[key]['process'].write(b"100 50\n")

                if StopFlag == 1:
                    new_position = QPointF(x, y)

                    # 清除上一个点的高亮
                    if temp_key_obj['fences'] != []:
                        for fence in temp_key_obj['fences']:
                            if fence != None:
                                self.scene().removeItem(fence)
                    temp_key_obj['fences'], temp_desc = self.fence_tool.highlight_fence_by_point(
                        new_position)

                    # 检查钥匙是否进入同心圆的圆环区域
                    # temp_key_obj['fences'].append(self.check_concentric_circles(
                    #     new_position))

                    x1 = x
                    y1 = y
                    if key == '鼠标':
                        y1 = -y
                    text = f'{key}: x:{x1:.2f},y:{y1:.2f}'
                    if temp_desc != '':
                        text += f' : {temp_desc}'
                    if temp_key_obj['list_text_item'] == None:
                        self.floatList.add_item('')

                        temp_key_obj['list_text_item'] = self.floatList.add_item(
                            text, temp_key_obj['color'])
                    else:
                        self.floatList.updateItemByIndex(
                            temp_key_obj['list_text_item'], text)
                    if key != 'UWB1':
                        # 由于pyqt坐标系y轴相反，特将y转为负值，但计算角度时还原成原始值
                        start, end = lightCalculator.calculate_start_end_input_xy(
                            x, -y)
                        # angle = self.calculate_angle(x, -y)
                        # self.set_angle(angle)
                        angle = self.calculate_angle_1(x, -y)
                        distance = math.sqrt(x**2 + y**2)
                        
                        self.data_queue.put(
                            {"x": x, "y": y, "angle": 360-angle, "distance": distance})

                        # num = self.lightCa.calculate_num_led(x, y)
                        self.manager.send_data(f'{start},{end}+')

                    if temp_key_obj['temp_line']:
                        self.scene().removeItem(temp_key_obj['temp_line'])
                    # 绘制从主驾车门到当前点位置的线
                    temp_key_obj['temp_line'] = self.scene().addLine(0, -200,
                                                                     x, y, QPen(Qt.gray, 3))
                    # self.fence_tool.find_fences(['0x2','0x4'])

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

                else:
                    # self.set_angle(0)
                    self.total_angle = 0
                    self.previous_angle = 0
                    # self.manager.send_data(f'#{int(self.total_angle)}!')

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
