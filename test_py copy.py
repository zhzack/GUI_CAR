from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QDialogButtonBox, QInputDialog

def show_input_dialog(parent=None, default_name=""):
    # 创建 QDialog 对象
    dialog = QDialog(parent)
    dialog.setWindowTitle("命名电子围栏")
    
    # 创建布局
    layout = QVBoxLayout()
    
    # 使用 QFormLayout 来管理标签和输入框
    form_layout = QFormLayout()
    
    # 第一个输入框：电子围栏名称
    input_name = QLineEdit(default_name)
    form_layout.addRow("请输入电子围栏名称:", input_name)
    
    # 第二个输入框：电子围栏描述
    input_desc = QLineEdit()
    form_layout.addRow("请输入电子围栏描述:", input_desc)
    
    # 将 form_layout 添加到主布局中
    layout.addLayout(form_layout)
    
    # 创建按钮框
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    layout.addWidget(buttons)
    
    # 按钮点击事件
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    
    dialog.setLayout(layout)

    # 显示对话框并获取输入值
    if dialog.exec_() == QDialog.Accepted:
        name = input_name.text()
        desc = input_desc.text()
        return name, desc
    return None, None

if __name__ == "__main__":
    app = QApplication([])

    # 调用对话框，传入默认的电子围栏名称
    name, desc = show_input_dialog(None, "默认电子围栏名称")
    
    if name:
        print(f"电子围栏名称: {name}")
        print(f"电子围栏描述: {desc}")

    app.exec_()
