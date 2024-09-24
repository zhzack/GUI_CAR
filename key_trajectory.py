import random
import time
from multiprocessing import Queue


def generate_key_trajectory(queue):
    """生成连续的钥匙轨迹并将其放入队列中"""
    # 初始位置，假设在画布的中间
    x, y = 0, 0
    while True:
        # 随机生成移动的偏移量，使轨迹更连续
        dx = random.randint(-145, 145)  # 每次移动较小的距离
        dy = random.randint(-145, 145)

        # 更新新的坐标
        x += dx
        y += dy

        # 保证x, y不超出画布的范围
        x = max(-550, min(x, 550))
        y = max(-550, min(y, 550))
        
        # x=-100
        # y=-80

        # 将新的坐标发送到队列
        queue.put((x, -y))
        time.sleep(0.2)  # 更小的间隔时间，使轨迹更加平滑
