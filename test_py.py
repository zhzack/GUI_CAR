from PyQt5.QtWidgets import QGraphicsView, QLabel, QVBoxLayout
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF, QPoint

from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPolygonF, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QPointF
import sys

class CarCanvas(QGraphicsView):
    def __init__(self, scene, parent=None):
        super(CarCanvas, self).__init__(scene, parent)
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        self.points = []  # 存储鼠标点击的坐标
        self.lines = []   # 存储围栏的边线
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件，获取点击位置"""
        # 获取点击的场景坐标
        scene_pos = self.mapToScene(event.pos())
        
        # 添加一个圆形来表示电子围栏的顶点
        point = QGraphicsEllipseItem(scene_pos.x() - 5, scene_pos.y() - 5, 10, 10)
        point.setBrush(QBrush(Qt.red))
        self.scene().addItem(point)
        
        # 将顶点添加到点列表中
        self.points.append(scene_pos)
        
        # 如果有至少两个点，连接它们
        if len(self.points) > 1:
            last_point = self.points[-2]
            current_point = self.points[-1]
            line = self.scene().addLine(last_point.x(), last_point.y(), current_point.x(), current_point.y(), QPen(Qt.blue, 2))
            self.lines.append(line)
        
        # 如果点的数量大于等于3，可以选择形成一个闭合的围栏
        if len(self.points) >= 3:
            self.check_if_fence_closed()
    
    def check_if_fence_closed(self):
        """检查是否形成闭合围栏，并高亮区域"""
        # 判断是否形成闭合区域
        first_point = self.points[0]
        last_point = self.points[-1]
        distance = ((last_point.x() - first_point.x())**2 + (last_point.y() - first_point.y())**2)**0.5
        
        # 如果最后一个点距离第一个点较近，认为围栏已经闭合
        if distance < 10:
            # 闭合围栏，连接最后一个点和第一个点
            self.scene().addLine(last_point.x(), last_point.y(), first_point.x(), first_point.y(), QPen(Qt.green, 2))
            
            # 可以在此处添加逻辑以高亮区域或设置警戒逻辑

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("电子围栏")
        
        # 创建场景和画布
        self.scene = QGraphicsScene(self)
        self.canvas = CarCanvas(self.scene, self)
        self.setCentralWidget(self.canvas)
        
        # 设置场景的范围
        self.scene.setSceneRect(0, 0, 800, 600)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
