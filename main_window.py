from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush
from PyQt5.QtCore import Qt, QPointF, QTimer
from multiprocessing import Process, Queue
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtCore import Qt

from car_canvas import CarCanvas

class MainWindow(QMainWindow):
    def __init__(self, queue):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Car and Key Position")
        self.queue = queue  # 获取共享队列

        # 创建场景和画布
        self.scene = QGraphicsScene(self)
        self.canvas = CarCanvas(self.scene, self)

        # # 加载汽车图像
        # car_pixmap = QPixmap('car_image.png')
        # car_item = QGraphicsPixmapItem(car_pixmap)
        # self.scene.addItem(car_item)
        
        
        # 加载汽车图像
        car_pixmap = QPixmap('car_image.png')
        car_item = QGraphicsPixmapItem(car_pixmap)

        # 设置图像的比例
        car_item.setScale(0.8)  # 设置缩放比例，例如0.5表示缩小一半

        # 旋转图像
        # car_item.setRotation(45)  # 旋转45度

        # 设置图像的初始位置
        car_item.setPos(-140, -240)

        # 将图像添加到场景中，并设置 z 值为较低的数值
        car_item.setZValue(-1000)  # 将 car_item 设置为最下层
        # 将图像添加到场景中
        self.scene.addItem(car_item)
        
        

        # 使用布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 设置默认窗口大小
        self.resize(1920, 1080)

        # 使用定时器定期检查队列是否有新位置
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_key_position)
        self.timer.start(50)  # 每50毫秒检查一次队列

    def update_key_position(self):
        """更新钥匙位置"""
        if not self.queue.empty():
            x, y = self.queue.get()
            self.canvas.set_key_position(x, y)
