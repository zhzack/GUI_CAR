import sys
from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView, QListWidget, QGraphicsProxyWidget, QPushButton, QVBoxLayout, QWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QFont


class CustomFloatList(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.W = 450
        self.H = 500

        # self.move(-int(parent.width()/2), int(parent.height()/2))
        # self.move(200,100)
        print(parent.width(), parent.height())
        # 设置透明背景
        self.setStyleSheet("background: transparent; border: none;")
        # self.setStyleSheet("border: none;")
        self.setFixedSize(self.W, self.H)

        # 创建列表
        self.data_list = QListWidget()
        self.data_list.setFixedSize(self.W, self.H)
        self.data_list.setStyleSheet("""
            QListWidget {
                background-color: #e0e0e0;  /* 背景色 */
                border: 2px solid #ccc;     /* 边框 */
                border-radius: 10px;        /* 圆角 */
            }
            QListWidget::item {
                background-color: #f0f0f0;    /* 每一项的背景色 */
                margin: 2px;
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0;  /* 鼠标悬停时的背景色 */
            }
            QListWidget::item:selected {
                background-color: #009688;  /* 选中项的背景色 */
                color: white;               /* 选中项的字体颜色 */
            }
        """)

        self.add_item("位置坐标或范围显示", QColor(0, 0, 255), QFont(
            "Courier New", 16))       # 蓝色字体，Courier

        # self.test_add()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.data_list)
        layout.setAlignment(Qt.AlignTop)

    def test_add(self):
        for i in range(1, 10):
            self.addData(i)

    def add_item(self, text, color, font=QFont(
            "Arial", 14, QFont.Bold)):
        """动态添加内容到列表"""
        new_data = f"{text}"
        self.data_list.addItem(new_data)
        row_count = self.data_list.count()-1
        item = self.data_list.item(row_count)
        item.setForeground(color)  # 设置文字颜色
        item.setFont(font)        # 设置字体

        self.auto_height()

        return self.data_list.count()-1

    def addData(self, text, color=QColor(0, 0, 255), font=QFont(
            "Arial", 14, QFont.Bold)):
        """动态添加内容到列表"""
        new_data = f"Data {text}"
        self.data_list.addItem(new_data)
        row_count = self.data_list.count()-1
        item = self.data_list.item(row_count)
        item.setForeground(color)  # 设置文字颜色
        item.setFont(font)

        self.auto_height()
        return item

    def auto_height(self):
        # 获取QListWidget中的项数量
        row_count = self.data_list.count()+1

        # 获取每行的推荐高度
        row_height = self.data_list.sizeHintForRow(0)

        self.setFixedHeight(row_height * row_count)

        # 设置固定高度，保证所有项都能显示
        self.data_list.setFixedHeight(row_height * row_count)

    def showRowCount(self):
        """显示当前行数"""
        row_count = self.data_list.count()
        print(f"当前列表有 {row_count} 行数据")

    def clearList(self):
        self.data_list.clear()

    def updateItemByIndex(self, index, text):
        item = self.data_list.item(index)  # 获取第一个条目
        item.setText(text)

    def getItemByIndex(self, index):
        item = self.data_list.item(index)
        return item
