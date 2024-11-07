import random
import time
from multiprocessing import Queue
from CreatJsonforCirclePath import generate_circular_trajectory_json, generate_linear_trajectory_json, generate_linears_trajectory_json
import json
import math
import csv
import os
import numpy as np
from movingAverage import MovingAverage

points = []
# def generate_key_trajectory(data, process_function):
#     """通用处理函数"""
#     result = process_function(data)
#     return result

# def generate_key_trajectory(queue):
#     """生成连续的钥匙轨迹并将其放入队列中"""
#     # 初始位置，假设在画布的中间
#     x, y = 0, 0
#     while True:
#         # 随机生成移动的偏移量，使轨迹更连续
#         dx = random.randint(-145, 145)  # 每次移动较小的距离
#         dy = random.randint(-145, 145)

#         # 更新新的坐标
#         x += dx
#         y += dy

#         # 保证x, y不超出画布的范围
#         x = max(-550, min(x, 550))
#         y = max(-550, min(y, 550))

#         # x=0
#         # y=-100

#         # 将新的坐标发送到队列
#         queue.put((x, -y))
#         time.sleep(0.2)  # 更小的间隔时间，使轨迹更加平滑


# def read_task_file(file_path, task_queue):
#     """读取任务文件并将每个任务放入队列中"""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             for node in data.get("nodes", []):
#                 task_queue.put(node)
#     except Exception as e:
#         print(f"读取任务文件时出错: {e}")


# def generate_key_trajectory(q):
#     file_path = "CreatJsonforCirclePath/cir.json"
#     """读取任务文件并提取节点数据"""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             nodes = data.get("nodes", [])
#             for node in nodes:
#                 position = node.get('pos')
#                 if position:
#                     x = position.get('x')*100
#                     y = position.get('y')*100
#                     points.append((x, y))
#                     q.put((x, y, 0, 0))
#     except Exception as e:
#         print(f"读取任务文件时出错: {e}")
# 正侧面60度
def process_degree_direct_60(degree1, degree2, degree3):
    values = [degree1, degree2, degree3]
    sorted_values = sorted(values, reverse=1)  # 降序

    if sorted_values == [degree3, degree1, degree2]:
        return sorted_values[1], +60, 1

    elif sorted_values == [degree1, degree3, degree2]:
        return -sorted_values[1], 60+60, 2

    elif sorted_values == [degree1, degree2, degree3]:
        return sorted_values[1], 60+60+60, 3

    elif sorted_values == [degree2, degree1, degree3]:
        return -sorted_values[1], 60+60+60+60, 4

    elif sorted_values == [degree2, degree3, degree1]:
        return sorted_values[1], 60+60+60+60+60, 5

    elif sorted_values == [degree3, degree2, degree1]:
        return -sorted_values[1], 60+60+60+60+60+60, 6


def process_pdoaToAng(pdoa_first, pdoa_second, pdoa_third):
    # 01 20 12
    # print(pdoa_first,pdoa_second,pdoa_third)
    def limit_value(value):
        if value > 180:
            return 1
        elif value < -180:
            return -1
        else:
            return value/180

    pdoa_first = limit_value(pdoa_first)
    pdoa_second = limit_value(pdoa_second)
    pdoa_third = limit_value(pdoa_third)

    # Custom3DPlot.process_values(pdoa_first,pdoa_second,pdoa_third)
    # pdoa_ressult,pdoa_offset=process_values(pdoa_first, pdoa_third,pdoa_second)

    # print(f"np.arcsin(pdoa_first):{np.arcsin(pdoa_first)}")
    # print(f"np.arcsin(pdoa_second):{np.arcsin(pdoa_second)}")
    # print(f"np.arcsin(pdoa_third):{np.arcsin(pdoa_third)}")

    arcsin_degrees1 = np.degrees(np.arcsin(pdoa_first))
    arcsin_degrees2 = np.degrees(np.arcsin(pdoa_second))
    arcsin_degrees3 = np.degrees(np.arcsin(pdoa_third))
    # print(f"arcsin_degrees1:{arcsin_degrees1}")
    # print(f"arcsin_degrees2:{arcsin_degrees2}")
    # print(f"arcsin_degrees3:{arcsin_degrees3}")

    degree_result, degree_offset, x = process_degree_direct_60(
        arcsin_degrees1, arcsin_degrees2, arcsin_degrees3)
    # print(degree_result,degree_offset+120)
    # print(degree_result)
    # print(x)
    return (degree_result+degree_offset+30) % 360
    return (degree_result+degree_offset) % 360, x, degree_offset, degree_result, arcsin_degrees1, arcsin_degrees2, arcsin_degrees3


def spherical_to_cartesian(azimuth, distance, elevation=0):
    # 将角度转换为弧度
    azimuth_rad = math.radians(azimuth)
    elevation_rad = math.radians(elevation)

    # 计算x, y, z
    x = distance * math.cos(elevation_rad) * math.cos(azimuth_rad)
    y = distance * math.cos(elevation_rad) * math.sin(azimuth_rad)
    z = distance * math.sin(elevation_rad)
    return x, y, z


def update_pdoa(last_pdoa, pdoa, abs_pdoa):
    # print("last_pdoa, pdoa, abs_pdoa:",last_pdoa, pdoa, abs_pdoa)
    if abs_pdoa >= 100 and last_pdoa - pdoa > 0:
        pdoa += abs_pdoa
        last_pdoa = pdoa
    else:
        last_pdoa -= abs_pdoa
        pdoa = last_pdoa
    return last_pdoa, pdoa


def read_csv_and_put_in_queue(queue, pdoa_queue):
    """
    读取 CSV 文件中的 x 和 y 列数据，并放入队列。
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    path = '不同距离绕圈'
    file_name = '绕圈10301435两移远新板子.csv'
    path = '8m绕圈'
    file_name = '8m绕圈两端新移远i平放1543.csv'
    path = '拉距'
    file_name = '两端旧移远1415.csv'
    csv_file_path = os.path.join(
        current_path, 'show_data_path', path, file_name)
    str_uwb_distance = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_distance'
    str_Carsts_X = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CarSts::Carsts_X'
    str_Carsts_Y = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CarSts::Carsts_Y'

    str_uwb_x = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_x'
    str_uwb_y = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_y'
    str_pdoa20 = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa20'
    str_pdoa12 = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa12'
    str_pdoa01 = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa01'
    # 初始化 last_pdoa_XX 变量用于保存上一次的值
    last_pdoa_20 = 0
    last_pdoa_12 = 0
    last_pdoa_01 = 0
    last_index = 0  # 标记第一次读取的数据

    # 滑动平均窗口大小
    window_size = 10  # 设置窗口大小为5

    # 用来跟踪异常值的阈值
    threshold_factor = 2  # 偏差的阈值因子，表示差异大于平均值的两倍为异常值

    # 创建滑动平均对象
    ma_pdoa_20 = MovingAverage(window_size, threshold_factor)
    ma_pdoa_01 = MovingAverage(window_size, threshold_factor)
    ma_pdoa_12 = MovingAverage(window_size, threshold_factor)
    ma_uwb_distance = MovingAverage(window_size, threshold_factor)

    # try:
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)  # 使用 DictReader 更方便读取列名
        for row in reader:
            # 获取 x、y、pdoa 值，并做空值检查
            try:
                # 替换 'str_pdoa20' 为实际列名
                pdoa_20 = float(row[str_pdoa20].strip())
                # 替换 'str_pdoa12' 为实际列名
                pdoa_12 = float(row[str_pdoa12].strip())
                # 替换 'str_pdoa01' 为实际列名
                pdoa_01 = float(row[str_pdoa01].strip())
                # 替换 'str_pdoa01' 为实际列名
                uwb_distance = float(row[str_uwb_distance].strip())

            except ValueError:
                # print("跳过无效数据行：", row)
                continue  # 如果数据无法转换为浮动数值则跳过这一行

            # 第一次循环时初始化
            if last_index == 0:
                last_pdoa_01 = pdoa_01
                last_pdoa_12 = pdoa_12
                last_pdoa_20 = pdoa_20
                last_index = 1
                # print(f"第一次读取数据: pdoa_01: {pdoa_01}, pdoa_12: {pdoa_12}, pdoa_20: {pdoa_20}")
            else:
                # 从第二行开始计算差值
                diff_pdoa_20 = abs(pdoa_20 - last_pdoa_20)
                diff_pdoa_12 = abs(pdoa_12 - last_pdoa_12)
                diff_pdoa_01 = abs(pdoa_01 - last_pdoa_01)

                # print(f"差值计算: pdoa_01: {last_pdoa_01}, pdoa_12: {
                #       diff_pdoa_12}, pdoa_20: {diff_pdoa_20}")

                diff = 300
                # # 更新上一行的数据
                if last_pdoa_01 > pdoa_01 and diff_pdoa_01 > diff:
                    pdoa_01 = pdoa_01+diff_pdoa_01
                elif last_pdoa_01 < pdoa_01 and diff_pdoa_01 > diff:
                    pdoa_01 = pdoa_01-diff_pdoa_01

                if last_pdoa_12 > pdoa_12 and diff_pdoa_12 > diff:
                    pdoa_12 = pdoa_12+diff_pdoa_12
                elif last_pdoa_12 < pdoa_12 and diff_pdoa_12 > diff:
                    pdoa_12 = pdoa_12-diff_pdoa_12

                if last_pdoa_20 > pdoa_20 and diff_pdoa_20 > diff:
                    pdoa_20 = pdoa_20+diff_pdoa_20
                elif last_pdoa_20 < pdoa_20 and diff_pdoa_20 > diff:
                    pdoa_20 = pdoa_20-diff_pdoa_20

                # if ma_pdoa_20.get_average():
                #     # 假设偏差超过阈值是异常值
                #     if abs(pdoa_20 - ma_pdoa_20.get_average()) > threshold_factor * np.std(ma_pdoa_20.data):
                #         print(f"异常值检测 - pdoa_20: {pdoa_20} 被视为异常")
                #         continue  # 跳过该数据点

                #     if abs(pdoa_01 - ma_pdoa_01.get_average()) > threshold_factor * np.std(ma_pdoa_01.data):
                #         print(f"异常值检测 - pdoa_01: {pdoa_01} 被视为异常")
                #         continue  # 跳过该数据点

                #     if abs(pdoa_12 - ma_pdoa_12.get_average()) > threshold_factor * np.std(ma_pdoa_12.data):
                #         print(f"异常值检测 - pdoa_12: {pdoa_12} 被视为异常")
                #         continue  # 跳过该数据点

                # 滑动平均更新
                pdoa_20 = ma_pdoa_20.update(pdoa_20)
                pdoa_01 = ma_pdoa_01.update(pdoa_01)
                pdoa_12 = ma_pdoa_12.update(pdoa_12)
                uwb_distance = ma_uwb_distance.update(uwb_distance)

                pdoa_queue.put((pdoa_01, pdoa_12, pdoa_20))

                last_pdoa_20 = pdoa_20
                last_pdoa_01 = pdoa_01
                last_pdoa_12 = pdoa_12
            # print(pdoa_20)
            azimuth = process_pdoaToAng(pdoa_01, pdoa_20, pdoa_12)
            x, y, z = spherical_to_cartesian(azimuth, uwb_distance)
            # print(x,y)

            # # 尝试将 x 和 y 转换为浮动类型，如果失败，则跳过该行
            x = float(x)
            y = float(y)

            # 将 (x, y) 数据放入队列
            queue.put((x, y))
            # except ValueError:
            #     # 如果转换失败（例如空字符串），则跳过当前行
            #     print("sdd")
            #     continue
    # except Exception as e:
    #     print(f"读取 CSV 文件时发生错误: {e}")


def generate_key_trajectory(q):
    file_path = "CreatJsonforCirclePath/cir_l.json"
    """读取任务文件并提取节点数据"""

    # 生成直线轨迹的JSON
    start = (0, 0)  # 起点
    end = (0, 4)    # 终点

    data = generate_circular_trajectory_json(6)
    data = data[0]  # 取出 JSON 字符串
    # print(json_data)

    # data = generate_linear_trajectory_json(start, end)
    # , ((4, 5), (0, 5)),((0, 0), (4, 0))
    segments = [((0, 0), (4, 0)), ((4, 5), (0, 5)), ((0, 0), (4, 0))]
    segments = [((0, 0), (5, 0)), ((5, 4), (0, 4)), ((0, 8), (5, 8)), ((5, 2), (0, 2)), ((0, 6), (5, 6)), ((
        5, 1), (0, 1)), ((0, 5), (5, 5)), ((5, 9), (0, 9)), ((0, 3), (5, 3)), ((5, 7), (0, 7))]

    x = 3.5
    segments = [((0,  0), (4, 0)),  ((4, 5-2), (1, 5-2)),
                ((1, 0), (x, 0)), ((x, 6-2),  (1,  6-2)),
                ((1, -2+1), (x, -2+1)), ((x, 7-2),  (1,  7-2)),
                ((1, -3+1), (x, -3+1)), ((x, 8-2),  (1,  8-2)),
                ((1, -4+1), (x, -4+1)), ((x, 9-2),  (1,  9-2)),
                ((1, -5+1), (x, -5+1)), ((x, 10-2), (1, 10-2)),
                ((1, -6+1), (x, -6+1)), ((x, 11-2), (1, 11-2)),
                ((1, -7+1), (x, -7+1)), ((x, 12-2), (1, 12-2)),
                ((1, -8+1), (x, -8+1)), ((x, 13-2), (1, 13-2)),
                ((1, -9+1), (x, -9+1)), ((x, 14-2), (1, 14-2)),
                ]
    # segments = generate_segments(6, 1, 6)

    data = generate_linears_trajectory_json(segments)
    data = json.loads(data)  # 解析 JSON 字符串

    # print(data)
    nodes = data.get("nodes", [])
    for node in nodes:
        position = node.get('pos')
        if position:
            x = position.get('x')*100
            y = position.get('y')*100
            points.append((x, y))

            # q.put((-y+150, x-267, -y+150, x-267,))
            # q.put((x, y, 0, 0))


# def generate_key_trajectory(q):
#     """生成连续的钥匙轨迹并将其放入队列中"""
#     trajectory = [
#         (-2000, 0, 0),      # 起始位置
#         (-150, 50, 2.5),    # 驾驶座车门
#         (-50, 50, 1.5),     # 驾驶座
#         (50, 50, 1.5),      # 副驾驶
#         (50, 150, 1.5),     # 右后座
#         (-50, 150, 1.5),    # 左后座
#         (-150, 150, 1.5),   # 左后座车门
#         (-150, 400, 0.5),   # 车子左后方
#         (-0, 400, 1.5),     # 车子正后方
#         (150, 400, 0.5),    # 车子右后方
#         (150, 50, 1.5),     # 副驾驶座车门
#         (2000, 0, 0),       # 结束位置
#     ]

#     speed = 100  # 设置移动速度（单位：像素/秒）

#     for i in range(len(trajectory) - 1):
#         start_x, start_y, _ = trajectory[i]
#         end_x, end_y, delay = trajectory[i + 1]

#         # 计算距离
#         distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)

#         # 计算移动时间
#         move_time = distance / speed  # 秒

#         steps_per_move = 200  # 每个移动的步数
#         step_x = (end_x - start_x) / steps_per_move
#         step_y = (end_y - start_y) / steps_per_move

#         # 在两个点之间移动
#         for step in range(steps_per_move):
#             x = start_x + step * step_x
#             y = start_y + step * step_y

#             # 添加随机跳动
#             jitter_x = random.uniform(-3, 3)  # 减小抖动幅度
#             jitter_y = random.uniform(-3, 3)

#             q.put((x + jitter_x, y + jitter_y, x, y))  # 负y值处理
#             time.sleep(move_time / steps_per_move)

#         # 停留时间
#         if delay > 0:
#             time.sleep(delay)
