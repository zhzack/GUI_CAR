from multiprocessing import Process, Queue
from PyQt5.QtCore import Qt, QTimer
from mqtt_client import MQTTClient


def readtData():
    if not queue.empty():
        # 从队列中获取数据并更新位置
        data = queue.get()
        print(f"Received data: {data}")


if __name__ == '__main__':

    # 创建一个队列用于跨进程通信
    queue = Queue()

    mqtt_client = MQTTClient(queue)
    mqtt_client.connect()
    mqtt_client.subscribe(
        mqtt_client.robot_topics + list(mqtt_client.res_topics.values()))

    while(1):
        readtData()
