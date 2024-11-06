import numpy as np
from collections import deque

# 滑动平均计算类


class MovingAverage:
    def __init__(self, window_size,threshold_factor=2):
        self.window_size = window_size
        self.data = deque(maxlen=window_size)  # 使用队列保存滑动窗口数据
        self.threshold_factor=threshold_factor

    def update(self, value):
        avg_value = self.get_average()
        if avg_value:
            if abs(value - avg_value) > self.threshold_factor * avg_value:
                return avg_value
        self.data.append(value)  # 加入新数据点
        return np.mean(self.data)  # 返回当前窗口的平均值

    def get_average(self):
        return np.mean(self.data) if len(self.data) > 0 else None  # 返回当前平均值
