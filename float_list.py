import sys
from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView, QListWidget, QGraphicsProxyWidget, QPushButton, QVBoxLayout, QWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QFont
from PyQt5.QtWidgets import QGraphicsView, QListWidget, QVBoxLayout, QListWidgetItem
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont


class CustomFloatList(QGraphicsView):
    def __init__(self, scene, title, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.W = 600
        self.H = 600

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
                # background-color: #f0f0f0;    /* 每一项的背景色 */
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

        self.add_item(title, QColor(0, 0, 255), QFont(
            "Courier New", 16))       # 蓝色字体，Courier

        # self.test_add()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.data_list)
        layout.setAlignment(Qt.AlignTop)

        # 定时器和状态变量
        self.blink_timer = QTimer(self)
        self.blinking = False
        self.blink_item = None  # 存储要闪烁的 item

        # 每 500 毫秒切换一次闪烁状态
        self.blink_timer.timeout.connect(self.stop_blink)

    def test_add(self):
        for i in range(1, 10):
            self.addData(i)

    def add_item(self, text, color=QColor(0, 0, 255), font=QFont("Arial", 18, QFont.Bold)):
        """动态添加内容到列表"""
        new_data = f"{text}"
        self.data_list.addItem(new_data)
        
        row_count = self.data_list.count() - 1
        item = self.data_list.item(row_count)
        
        # 设置文字颜色
        item.setForeground(color)
        
        # 设置字体
        item.setFont(font)
        
        # 设置背景色（可以覆盖样式表的设置）
        item.setBackground(QColor(240, 240, 240))  # 你可以根据需要自定义背景色
        
        self.auto_height()
        
        return row_count  # 返回当前添加的项的索引

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
        row_count = self.data_list.count()+2

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

    def start_blink(self, index):
        item = self.data_list.item(index)
        print(1)

        """启动闪烁效果"""
        self.blink_item = item  # 保存要闪烁的 item
        self.blinking = True    # 设置初始闪烁状态为 False
        self.blink_item.setData(Qt.BackgroundRole, QColor(240, 0, 0, 90))

        self.blink_timer.start(500)  # 启动定时器，500毫秒切换一次闪烁状态

    def stop_blink(self):
        """停止闪烁效果"""
        print(2)

        self.blink_timer.stop()  # 停止定时器
        if self.blink_item:
            self.blink_item.setData(
                Qt.BackgroundRole, QColor(240, 240, 240))  # 恢复背景色
            self.blink_item = None  # 清空闪烁项

    def toggle_blink(self):
        """切换闪烁效果"""
        if self.blink_item:
            if self.blinking:
                # 恢复正常背景色
                self.blink_item.setBackground(QColor(240, 240, 240))
            else:
                # 设置为闪烁的背景色（例如红色）
                self.blink_item.setBackground(QColor(255, 0, 0))

            # 切换闪烁状态
            self.blinking = not self.blinking
