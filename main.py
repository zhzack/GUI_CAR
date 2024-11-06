import sys
from PyQt5.QtWidgets import QApplication
from multiprocessing import Process, Queue
from main_window import MainWindow
import key_trajectory

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 创建一个队列用于跨进程通信
    queue = Queue()

    # 创建生成轨迹的子进程
    # trajectory_process = Process(target=key_trajectory.generate_key_trajectory, args=(queue,))
    trajectory_process = Process(target=key_trajectory.read_csv_and_put_in_queue, args=(queue,))
    trajectory_process.start()

    # 创建主窗口并传递队列
    window = MainWindow(queue)
    window.show()

    try:
        sys.exit(app.exec_())
    finally:
        # 退出时终止子进程
        trajectory_process.terminate()
        trajectory_process.join()
