from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF, QTimer
from multiprocessing import Process, Queue
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QGraphicsSceneMouseEvent
from fence_tool import FenceTool
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt, QRect
from car_canvas import CarCanvas


class MainWindow(QMainWindow):
    def __init__(self, queue):
        super(MainWindow, self).__init__()
        self.setWindowTitle("汽车和钥匙位置")
        self.queue = queue  # 获取共享队列

        # 创建场景和画布
        self.scene = QGraphicsScene(self)
        # 初始化电子围栏工具
        self.fence_tool = FenceTool(self.scene)
        self.canvas = CarCanvas(self.scene, self)

        # 加载汽车图像
        car_pixmap = QPixmap('car_image.png')
        car_item = QGraphicsPixmapItem(car_pixmap)

        # 设置图像的比例
        car_item.setScale(0.655)  # 设置缩放比例，例如0.5表示缩小一半

        # 旋转图像
        # car_item.setRotation(45)  # 旋转45度

        # 设置图像的初始位置
        car_item.setPos(-115, -210)
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
        self.resize(2560, 1440)

        # 使用定时器定期检查队列是否有新位置
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_key_position)
        self.timer.start(5)  # 每50毫秒检查一次队列

        # 添加电子围栏的菜单选项
        self.init_menu()

        self.canvas.setMouseTracking(True)
        # 主布局
        self.layout = QVBoxLayout(self)



    def init_menu(self):
        """创建菜单选项，选择电子围栏模式"""
        menu_bar = self.menuBar()
        fence_menu = menu_bar.addMenu('电子围栏')

        add_fence_action = QAction('手动输入', self)
        add_fence_action.triggered.connect(self.manual_input_fence)

        add_fence_by_mouse_action = QAction('通过鼠标添加', self)
        add_fence_by_mouse_action.triggered.connect(self.start_fence_by_mouse)

        fence_menu.addAction(add_fence_action)
        fence_menu.addAction(add_fence_by_mouse_action)

    def manual_input_fence(self):
        """手动输入围栏的顶点"""
        # 这里可以添加手动输入围栏顶点的代码

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
        if not self.queue.empty():
            x, y, x1, y1 = self.queue.get()
            self.lastpos = (x, y, x1, y1)
            self.canvas.set_key_position(x, -y, x1, y1)
        else:
            x, y, x1, y1 = self.lastpos
            self.canvas.set_key_position(x, -y, x1, y1)


        
