import sys
from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView, QListWidget, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        
        # 创建浮动的列表小部件
        self.data_list = QListWidget()
        self.data_list.addItems(["Data 1", "Data 2", "Data 3"])
        self.data_list.setFixedSize(200, 100)

        # 设置为视图内的浮动小部件
        self.overlay_widget = QWidget(self)
        layout = QVBoxLayout(self.overlay_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.data_list)
        self.overlay_widget.setFixedSize(200, 100)
        self.overlay_widget.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);")
        
        # 初始化位置
        self.updateOverlayPosition()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateOverlayPosition()

    def updateOverlayPosition(self):
        """更新浮动小部件的位置，固定在窗口右上角"""
        self.overlay_widget.move(self.width() - self.overlay_widget.width() - 10, 10)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建场景和视图
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 800, 600)
    view = CustomGraphicsView(scene)
    view.setScene(scene)

    # 显示窗口
    view.resize(800, 600)
    view.show()

    sys.exit(app.exec_())
