import sys
from PyQt5.QtWidgets import (
    QApplication, QGraphicsScene, QGraphicsView, QListWidget, QGraphicsProxyWidget, QPushButton, QVBoxLayout, QWidget,QListWidgetItem
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter,QFont

class CustomFloatList(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene

        # self.move(-int(parent.width()/2), int(parent.height()/2)) 
        # self.move(200,100) 
        print(parent.width(),parent.height()) 
         # 设置透明背景
        self.setStyleSheet("background: transparent; border: none;")
        # self.setStyleSheet("border: none;")
        # self.setFixedSize(500, 500)


        
        

        # 创建列表
        self.data_list = QListWidget()
        self.data_list.setFixedSize(500, 5000)
        self.data_list.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;  /* 背景色 */
                border: 2px solid #ccc;     /* 边框 */
                border-radius: 10px;        /* 圆角 */
            }
            QListWidget::item {
                background-color: white;    /* 每一项的背景色 */
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
        # 添加自定义项
        self.add_item("Item 1", QColor(255, 0, 0), QFont("Arial", 14, QFont.Bold))  # 红色字体，Arial粗体
        self.add_item("Item 2", QColor(0, 255, 0), QFont("Times New Roman", 12))   # 绿色字体，Times New Roman
        self.add_item("Item 3", QColor(0, 0, 255), QFont("Courier New", 16))       # 蓝色字体，Courier 
        
        self.test_add()

        # 获取QListWidget中的项数量
        row_count = self.data_list.count()

        # 获取每行的推荐高度
        row_height = self.data_list.sizeHintForRow(0)

        # 设置固定高度，保证所有项都能显示
        self.data_list.setFixedHeight(row_height * row_count)



        # 设置为视图内的浮动小部件
        self.overlay_widget = QWidget(self)
        layout = QVBoxLayout(self.overlay_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.data_list)
        self.overlay_widget.setFixedSize(200, 500)
        self.overlay_widget.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);")
         # 调整父控件的大小
        self.setSizeIncrement(100,100)  # 自动调整为包含的控件大小

        
        
        

        # # 添加到场景中
        # self.proxy_widget = QGraphicsProxyWidget()
        # self.proxy_widget.setWidget(self.data_list)
        # scene.addItem(self.proxy_widget)

        

        # 初始化位置
        # self.updateOverlayPosition()
        # self.overlay_widget.show()
        

        # # 添加一个测试按钮
        # self.button = QPushButton("Add Data")
        # self.button.clicked.connect(self.addData)
        # self.button_proxy = QGraphicsProxyWidget()
        # self.button_proxy.setWidget(self.button)
        # scene.addItem(self.button_proxy)
        # self.button_proxy.setPos(10, 10)

    def test_add(self):
        for i in range(1, 10):
            self.addData(i)

    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
        # self.data_list.move(self.width() - self.data_list.width() - 100, 10)
        # self.updateOverlayPosition()

    # def updateOverlayPosition(self):
    # #     """更新浮动小部件的位置，固定在窗口右上角"""
    #     self.overlay_widget.move(self.width() - self.overlay_widget.width() - 100, 10)

        # self.overlay_widget.move(
        #     200,  # 距右边框 10 像素
        #     10  # 距顶部 10 像素
        # )
    def add_item(self, text, color, font):
        """动态添加内容到列表"""
        new_data = f"Data {text}"
        self.data_list.addItem(new_data)
        row_count = self.data_list.count()-1
        item = self.data_list.item(row_count)
        # item = QListWidgetItem(text)
        item.setForeground(color)  # 设置文字颜色
        item.setFont(font)        # 设置字体

        return item
    

        item = QListWidgetItem(text)
        item.setTextColor(color)  # 设置文字颜色
        item.setFont(font)        # 设置字体
        self.data_list.addItem(item)


    def addData(self, text):
        """动态添加内容到列表"""
        new_data = f"Data {text}"
        self.data_list.addItem(new_data)
        row_count = self.data_list.count()-1
        item = self.data_list.item(row_count)
        item.setForeground(QColor(0, 0, 255))  # 设置文字颜色
        return item

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
