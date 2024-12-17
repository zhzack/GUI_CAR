from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPen, QBrush
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction
from fence_tool import FenceTool
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from car_canvas import CarCanvas
import os
import json

from PyQt5.QtWidgets import (
    QMainWindow,
    QDesktopWidget,
    QVBoxLayout,
    QWidget,
    QAction,
    QFileDialog,
    QDialog,
)
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
)
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QVBoxLayout,
)

from mqtt_client import MQTTClient

JsonforCPath = 'CreatJsonforCirclePath'


class MainWindow(QMainWindow):
    def __init__(self, queue):
        super(MainWindow, self).__init__()
        self.setWindowTitle("汽车和钥匙位置")
        self.queue = queue  # 获取共享队列
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        # print(self.robot_topics, self.res_topics)
        self.mqtt_res_obj = {}
        
        self.is_matt_connect = True

        if self.is_matt_connect:
            self.mqtt_client = MQTTClient(self.queue)
            self.mqtt_client.connect()

        # 创建场景和画布
        self.scene = QGraphicsScene(self)
        # 初始化电子围栏工具
        self.fence_tool = FenceTool(self.scene, self)
        self.canvas = CarCanvas(self.scene, self)
        self.canvas.queue = queue

        # 保存任务轨迹
        self.points = []

        # 加载汽车图像
        self.car_img = os.path.join(self.current_path, 'img', 'car_image.png')
        car_pixmap = QPixmap(self.car_img)
        self.zhaun_img = os.path.join(self.current_path, 'img', '石砖2.jpg')
        car_item = QGraphicsPixmapItem(car_pixmap)

        # 设置图像的比例
        car_item.setScale(0.655)  # 设置缩放比例，例如0.5表示缩小一半

        # 旋转图像
        # car_item.setRotation(45)  # 旋转45度

        # 设置图像的初始位置
        car_item.setPos(-115+90, -210-220)
        # car_item.setPos(0, 0)

        # 将图像添加到场景中，并设置 z 值为较低的数值
        car_item.setZValue(-1000)  # 将 car_item 设置为最下层
        # 将图像添加到场景中
        self.scene.addItem(car_item)
        self.lastpos = (1, 2, 3, 4)

        # 使用布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 设置默认窗口大小
        # self.resize(2560, 1440)
        # 获取屏幕的尺寸
        screen = QDesktopWidget().screenGeometry()

        # 获取窗口的尺寸
        window_size = self.geometry()

        # 计算窗口居中位置
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2

        # 移动窗口到居中位置
        self.move(x, y)

        # 窗口最大化显示
        self.showMaximized()

        # 使用定时器定期检查队列是否有新位置
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_key_position)
        self.timer.start(0)  # 每50毫秒检查一次队列

        # 添加电子围栏的菜单选项
        self.init_menu()

        self.canvas.setMouseTracking(True)
        # 主布局
        # self.layout = QVBoxLayout(self)
        self.show_coordinate_system = True  # 控制坐标系显示的变量

        # 绘制坐标系
        self.draw_coordinate_system()
        # 绘制背景
        # self.set_background_image()

    def set_background_image(self):

        image_path = self.zhaun_img
        """设置场景的背景图片并平铺"""
        # 加载图片
        pixmap = QPixmap(image_path)

        # 获取场景的边界
        scene_rect = self.scene.sceneRect()
        scene_width = scene_rect.width()
        scene_height = scene_rect.height()

        # 计算图片的重复次数
        image_width = pixmap.width()
        image_height = pixmap.height()

        # 平铺背景：在场景中添加多个 QGraphicsPixmapItem
        for x in range(-int(scene_width), int(scene_width), image_width):
            for y in range(-int(scene_height), int(scene_height), image_height):
                # 创建一个 QGraphicsPixmapItem，将图片放置到场景的相应位置
                pixmap_item = QGraphicsPixmapItem(pixmap)
                pixmap_item.setPos(x, y)  # 设置每个图片的位置
                pixmap_item.setZValue(-2000)
                self.scene.addItem(pixmap_item)

    def draw_coordinate_system(self):
        """绘制坐标系和网格线"""
        if not self.show_coordinate_system:
            return  # 如果不显示坐标系，直接返回

        # 设置网格线的样式
        pen = QPen(QColor(200, 200, 200))  # 浅灰色网格线
        pen.setStyle(Qt.DashLine)

        length = 30000
        part = 50

        # 绘制网格线：横线和竖线
        for x in range(-length, length, part):  # 每part单位画一条竖线
            self.scene.addLine(x, -length, x, length, pen)
        for y in range(-length, length, part):  # 每part单位画一条横线
            self.scene.addLine(-length, y, length, y, pen)

        # 绘制X轴和Y轴
        axis_pen = QPen(Qt.black)  # 黑色轴线
        self.scene.addLine(0, -length, 0, length, axis_pen)  # Y轴
        self.scene.addLine(-length, 0, length, 0, axis_pen)  # X轴

        # 设置刻度线的样式
        scale_pen = QPen(Qt.black)
        scale_font = self.canvas.font()  # 使用画布的字体

        # 绘制X轴刻度线和刻度值
        for x in range(-length, length, part):
            if x % 100 == 0:
                # 绘制X轴上的刻度线
                self.scene.addLine(x, 0, x, 10, scale_pen)  # 刻度线
                # 绘制刻度值
                text_item = self.scene.addText(str(x), scale_font)
                text_item.setPos(x-15, 10)  # 将文本位置稍微偏移
            else:
                # 绘制X轴上的刻度线
                self.scene.addLine(x, 0, x, 5, scale_pen)  # 刻度线

        # 绘制Y轴刻度线和刻度值
        for y in range(-length, length, part):
            if y % 100 == 0:
                # 绘制Y轴上的刻度线
                self.scene.addLine(0, y, 10, y, scale_pen)  # 刻度线
                # 绘制刻度值
                text_item = self.scene.addText(str(-y), scale_font)
                text_item.setPos(10, y-10)  # 将文本位置稍微偏移
            else:
                # 绘制Y轴上的刻度线
                self.scene.addLine(0, y, 5, y, scale_pen)  # 刻度线
                # 绘制刻度值
                # text_item = self.scene.addText(str(-y), scale_font)
                # text_item.setPos(5, y + 5)  # 将文本位置稍微偏移

        self.canvas.update()  # 更新画布，确保所有图形被绘制

    def toggle_coordinate_system(self):
        """切换坐标系的显示状态"""
        self.show_coordinate_system = not self.show_coordinate_system
        self.scene.clear()  # 清除当前场景
        self.draw_coordinate_system()  # 重新绘制坐标系
        self.canvas.update()  # 更新画布显示

    def init_menu(self):
        menu_bar = self.menuBar()
        menu_items = {
            '电子围栏': [
                ('手动输入', self.manual_input_fence),
                ('通过鼠标添加', self.start_fence_by_mouse),
            ],
            '设置': [
                ('鼠标模拟位置', self.setMouseMoveActive),
                ('设置选项2', self.manual_input_fence),
            ]
        }

        # 创建子菜单
        for menu_name, actions in menu_items.items():
            menu = menu_bar.addMenu(menu_name)
            for action_name, callback in actions:
                action = QAction(action_name, self)
                action.triggered.connect(callback)
                menu.addAction(action)

        # 需要直接添加到 menu_bar 的选项
        direct_actions = [
            ('小车任务配置', self.edit_task_set),
            ('开始任务', self.btn_start_stop_pause),
            ('暂停任务', self.btn_start_stop_pause),
            ('停止任务', self.btn_start_stop_pause),
            ('上传任务文件', self.btn_pub_send_task_file),
            ('设置任务轨迹', self.btn_set_task_path),
            ('清除任务轨迹', self.btn_remove_task_path),

        ]

        # 直接在菜单栏中添加多个选项
        for action_name, callback in direct_actions:
            option_action = QAction(action_name, self)
            option_action.triggered.connect(callback)
            menu_bar.addAction(option_action)

    def btn_remove_task_path(self):
        if self.points:
            for point in self.points:
                self.scene.removeItem(point)  # 从场景中移除点
            self.points.clear()  # 清空点的引用列表

    def btn_set_task_path(self):
        self.btn_remove_task_path()
        self.json_path = self.mqtt_client.config['pub_config']["task_set"]["task_set"]["task_file"]

        self.json_path = os.path.join(
            self.mqtt_client.current_path, JsonforCPath, self.json_path)

        print(self.json_path)
        with open(self.json_path, 'r') as file:
            self.data = json.load(file)
        #   用于存储添加的点
        for node in self.data["nodes"]:
            y = -node["pos"]["x"] * 100+267  # 缩放位置
            x = -node["pos"]["y"] * 100+145

            # x = -node["pos"]["y"] * 100+200  # 缩放位置
            # y = node["pos"]["x"] * 100-130

            # 判断是否有任务属性
            if "task" in node:
                point = QGraphicsEllipseItem(x, y, 10, 10)  # 任务点
                point.setBrush(QBrush(Qt.red))  # 用红色表示
            else:
                point = QGraphicsEllipseItem(x, y, 10, 10)  # 普通点
                point.setBrush(QBrush(Qt.green))  # 用蓝色表示

            self.scene.addItem(point)  # 添加到场景中
            self.points.append(point)  # 存储点的引用

    def btn_start_stop_pause(self):
        action = self.sender()
        print(f"点击了菜单项: {action.text()}")
        text = action.text()
        if text == '开始任务':
            self.mqtt_client.pub_task_control(1)
        elif text == '暂停任务':
            self.mqtt_client.pub_task_control(0)
        elif text == '停止任务':
            self.mqtt_client.pub_task_control(2)

    def open_file_dialog(self, file_name=False):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        current_path = os.path.dirname(os.path.realpath(__file__))
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            os.path.join(current_path, JsonforCPath),
            "JSON Files (*.json)",
            options=options,
        )
        if file_name:
            return os.path.basename(file_path)
        return file_path if file_path else None

    def btn_pub_send_task_file(self):
        file_path = self.open_file_dialog()
        if file_path:
            self.mqtt_client.pub_send_task_file(file_path)

    def edit_task_set(self):
        config = self.mqtt_client.config
        task_set_msg = config["pub_config"]["task_set"]["task_set"]

        dialog = QDialog()
        dialog.setWindowTitle("设置任务")
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        input_fields = {}

        for key, value in task_set_msg.items():
            if key == "task_file":
                file_button = QPushButton(task_set_msg["task_file"])
                file_button.clicked.connect(
                    lambda: file_button.setText(self.open_file_dialog(True))
                )
                form_layout.addRow(key, file_button)
                input_fields[key] = file_button
            else:
                input_field = QLineEdit(str(value))
                form_layout.addRow(key, input_field)
                input_fields[key] = input_field

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            for key, input_field in input_fields.items():
                if key == "task_file":
                    task_set_msg[key] = input_field.text()
                else:
                    task_set_msg[key] = input_field.text()
            self.mqtt_client.pub_task_control(2)
            self.mqtt_client.pub_task_set()
            return task_set_msg
        else:
            return None

    def setMouseMoveActive(self):
        # print(self.canvas.mouse_move_active)
        self.canvas.mouse_move_active = not self.canvas.mouse_move_active

    def manual_input_fence(self):
        """手动输入围栏的顶点"""
        # 这里可以添加手动输入围栏顶点的代码
        action = self.sender()
        print(f"点击了菜单项: {action.text()}")

    def start_fence_by_mouse(self):
        """通过鼠标点击添加围栏"""
        self.canvas.set_fence_mode(True)
        self.fence_tool.start()

    # def mousePressEvent(self, event):
    #     """处理鼠标点击事件，添加围栏顶点"""
    #     if self.canvas.fence_mode_active:
    #         if event.button() == Qt.RightButton:
    #             pos = self.canvas.mapToScene(event.pos())
    #             self.fence_tool.add_point(pos)
    #         elif event.button() == Qt.LeftButton and len(self.fence_tool.points) > 0:
    #             # 结束添加围栏
    #             self.canvas.set_fence_mode(False)

    # def mouseMoveEvent(self, event):
    #     print(self.mapToScene(event.pos()))
    #     if self.canvas.fence_mode_active:
    #         pos = self.canvas.mapToScene(event.pos())
    #         self.fence_tool.update_temp_line(pos)
    #         self.fence_tool.show_coordinates(pos)
    #         print(pos)

    def update_key_position(self):
        """更新钥匙位置"""
        while not self.queue.empty():
            object = self.queue.get()
            for value in object:
                # print(f"Value: {value}")
                if 'BLE' in value:
                    pass
                    self.canvas.set_ble_area(value)

                else:
                    self.canvas.set_key_position(value)
