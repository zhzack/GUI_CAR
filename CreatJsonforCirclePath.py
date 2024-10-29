import json
import os
import math
from datetime import datetime


def calculate_radius(start_point, end_point):
    # 计算起点和终点的距离
    distance = math.sqrt(
        (end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2)
    # 返回一半的距离作为半径
    return distance / 2


def calculate_arc_points(segment1, segment2, nodes=[], radius=2, arc_length=0.1):

    # 提取线段的起始点和结束点
    p1, p2 = segment1
    p3, p4 = segment2

    # 计算圆心
    center_x = (p2[0] + p3[0]) / 2
    center_y = (p2[1] + p3[1]) / 2

    # 计算起始角度
    start_angle = math.atan2(p2[1] - center_y, p2[0] - center_x)
    end_angle = math.atan2(p3[1] - center_y, p3[0] - center_x)

    # 确保起始角度减去90度
    start_angle -= math.pi / 2
    end_angle -= math.pi / 2

    # 计算步数
    num_nodes = int(abs(end_angle - start_angle) / (arc_length / radius)) + 1

    nodes = []
    for i in range(num_nodes + 1):
        angle = start_angle + (end_angle - start_angle) * (i / num_nodes)
        x = round(center_x + radius * math.cos(angle), 3)
        y = round(center_y + radius * math.sin(angle), 3)
        node = {"id": len(nodes) + 1, "pos": {"x": x, "y": y}}
        print(node)
        nodes.append(node)

    return nodes


def generate_line_nodes(start_point, end_point, nodes=[], arc_length=0.1):
    direction_vector = (end_point[0] - start_point[0],
                        end_point[1] - start_point[1])
    length = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
    unit_vector = (direction_vector[0] / length, direction_vector[1] / length)
    num_nodes = int(length / arc_length)

    for i in range(num_nodes + 1):
        x = round(start_point[0] + i * arc_length * unit_vector[0], 3)
        y = round(start_point[1] + i * arc_length * unit_vector[1], 3)
        node = {"id": i + 1, "pos": {"x": x, "y": y}}

        # 检查当前位置是否为特殊节点（每隔1米）
        # print(i * arc_length % 1 == 0)
        if x % 1 == 0:
            # 检查特殊节点是否已经在普通节点中
            # if not any(n['pos'] == {"x": x, "y": y} for n in nodes):
            lenth_nodes = len(nodes)
            if lenth_nodes == 0:
                lenth_nodes = 1
            else:
                lenth_nodes += 1
            special_node = {
                "id": lenth_nodes,  # 特殊节点的 id 从普通节点后续开始
                "pos": {"x": x, "y": y},
                "task": {
                    "task_id": lenth_nodes,
                    "is_pre_defined": False,
                    "defined_id": -1,
                    "repeat_count": 1,
                    "task_nodes": [
                        {
                            "arm_id": 1,
                            "stay_time": 3,
                            "arm_pose": {
                                "x": 0.04,
                                "y": 0.03,
                                "z": 0.49,
                                "roll": -89.96,
                                "pitch": -3.56,
                                "yaw": 88.89,
                                "joint1": -4.712,
                                "joint2": -2.870,
                                "joint3": 2.491,
                                "joint4": -2.727,
                                "joint5": 3.122,
                                "joint6": -0.026,
                            },
                        }
                    ],
                },
            }
            nodes.append(special_node)  # 直接添加到节点列表中
            # nodes.append(node)
        else:
            nodes.append(node)
    return nodes


def generate_linear_trajectory_json(start_point, end_point, nodes=[], arc_length=0.1):
    task_name = "LinearPath"
    nodes = generate_line_nodes(start_point, end_point, nodes)

    data = {"task_name": task_name, "nodes": nodes}
    return json.dumps(data, indent=4, ensure_ascii=False)


def calculate_angle(center, point):
    C_x, C_y = center
    P_x, P_y = point

    # 计算方向向量
    dx = P_x - C_x
    dy = P_y - C_y

    # 计算角度
    angle = math.atan2(dy, dx)

    return angle  # 返回值以弧度表示


def radians_to_degrees(radians):
    return radians * (180 / math.pi)


def generate_arc(start_point, end_point, nodes=[], rotation_direction=1, arc_length=0.1):

    radius = calculate_radius(start_point, end_point)
    # 计算圆心位置（在起始点和结束点的中间）
    center_x = (start_point[0] + end_point[0]) / 2
    center_y = (start_point[1] + end_point[1]) / 2

    angle_start = calculate_angle((center_x, center_y), start_point)
    angle_end = calculate_angle((center_x, center_y), end_point)

    # # # 计算起始和结束角度（半圆）
    # temp=angle_start
    # angle_start = angle_end
    # angle_end = temp
    # print(radians_to_degrees(angle_start))
    # print(radians_to_degrees(angle_end))
    # print(f"angle_start:{angle_start}")
    # print(f"angle_end:{angle_end}")

    arc_length_actual = math.pi * radius  # 半圆的弧长
    num_nodes = int(arc_length_actual / arc_length)
    rotation_direction = rotation_direction % 2
    # 生成节点
    for i in range(num_nodes + 1):
        # 根据旋转方向调整角度计算
        if rotation_direction == 1:  # 顺时针
            angle = angle_start + (angle_end - angle_start) * (i / num_nodes)
        else:  # 逆时针
            angle = angle_start - (angle_end - angle_start) * (i / num_nodes)

        x = round(center_x + radius * math.cos(angle), 3)
        y = round(center_y + radius * math.sin(angle), 3)
        node = {"id": len(nodes) + 1, "pos": {"x": x, "y": y}}
        if i % 10 == 0:
            lenth_nodes = len(nodes)
            special_node = {
                "id": lenth_nodes,  # 特殊节点的 id 从普通节点后续开始
                "pos": {"x": x, "y": y},
                "task": {
                    "task_id": lenth_nodes,
                    "is_pre_defined": False,
                    "defined_id": -1,
                    "repeat_count": 1,
                    "task_nodes": [
                        {
                            "arm_id": 1,
                            "stay_time": 3,
                            "arm_pose": {
                                "x": 0.04,
                                "y": 0.03,
                                "z": 0.49,
                                "roll": -89.96,
                                "pitch": -3.56,
                                "yaw": 88.89,
                                "joint1": -4.712,
                                "joint2": -2.870,
                                "joint3": 2.491,
                                "joint4": -2.727,
                                "joint5": 3.122,
                                "joint6": -0.026,
                            },
                        }
                    ],
                },
            }
            nodes.append(special_node)  # 直接添加到节点列表中
        else:
            nodes.append(node)

    return nodes


def generate_linears_trajectory_json(segments, arc_radius=2.0, arc_length=0.1):
    all_nodes = []  # 用于存储所有节点
    last_start_point = None
    last_end_point = None
    i = 1
    for start_point, end_point in segments:
        i += 1
        # 如果有前一段线段，则添加圆弧
        if last_start_point is not None and last_end_point is not None:

            all_nodes = generate_arc(
                last_end_point, start_point, all_nodes, i, arc_length)

        # 生成当前线段的节点并添加到总节点中
        all_nodes = generate_line_nodes(
            start_point, end_point, all_nodes)
        # print(len(all_nodes))

        # 更新最后的起始和结束点
        last_start_point = start_point
        last_end_point = end_point

    return json.dumps({"task_name": "PathWithArcs", "nodes": all_nodes}, ensure_ascii=False)

# 确保 generate_line_nodes 和 calculate_arc_points 都能正确返回更新后的 all_nodes


def generate_circular_trajectory_json(radius, arc_length=0.1):
    task_name = (
        "CirclePath_Rad" + str(radius) + "m"
    )  # _'+datetime.now().strftime("%Y-%m-%d-%H%M%S")
    center = (0, radius)  # 圆心位置
    # 计算圆的周长
    circumference = 2 * math.pi * radius
    # 计算节点数量
    num_nodes = int(circumference / arc_length)
    # 节点数组
    nodes = []
    # 小数保留位数
    PointNm = 3
    # 初始化下一个30度倍数的角度阈值
    next_special_angle = 30
    # 已添加节点的数量
    next_special_angle_id = 0
    # 停留时间，单位秒
    stay_time = 3

    # 任务点id，中途停顿时的taskid
    taskId_points = []
    # 计算并添加圆周上的节点和特殊节点
    for i in range(num_nodes + 2):  # 包括最后一个节点
        theta = arc_length / radius * i

        # 转换弧度到度数
        degrees = math.degrees(theta)
        # 检查是否超过了下一个30度的倍数阈值
        while degrees >= next_special_angle:
            # 计算30度的倍数点的坐标
            special_theta = math.radians(next_special_angle)
            special_x = round(center[0] + radius *
                              math.sin(special_theta), PointNm)
            special_y = round(center[1] - radius *
                              math.cos(special_theta), PointNm)
            taskId_points.append(i + 1 + next_special_angle_id)
            special_node = {
                "id": i + 1 + next_special_angle_id,
                "pos": {"x": special_x, "y": special_y},
                "task": {
                    "task_id": i + 1 + next_special_angle_id,
                    "is_pre_defined": False,
                    "defined_id": -1,
                    "repeat_count": 1,
                    "task_nodes": [
                        {
                            "arm_id": 1,
                            "stay_time": stay_time,
                            "arm_pose": {
                                "x": 0.04,
                                "y": 0.03,
                                "z": 0.49,
                                "roll": -89.96,
                                "pitch": -3.56,
                                "yaw": 88.89,
                                "joint1": -4.712,
                                "joint2": -2.870,
                                "joint3": 2.491,
                                "joint4": -2.727,
                                "joint5": 3.122,
                                "joint6": -0.026,
                            },
                        }
                    ],
                },
            }
            nodes.append(special_node)
            next_special_angle_id += 1
            # 增加下一个30度的倍数
            next_special_angle += 30
            continue
        if math.degrees(theta) < 360:
            x = round(center[0] + radius * math.sin(theta), PointNm)
            y = round(center[1] - radius * math.cos(theta), PointNm)
            node = {"id": i + 1 + next_special_angle_id,
                    "pos": {"x": x, "y": y}}
            nodes.append(node)
    data = {"task_name": task_name, "nodes": nodes}

    return json.dumps(data, indent=4, ensure_ascii=False), taskId_points


def save_json_to_file(json_data, task_name):
    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    # 获取当前文件名（不含扩展名）
    current_file_name = os.path.splitext(os.path.basename(__file__))[0]

    # 组合文件夹名称
    folder_name = f"{current_file_name}_{current_date}"
    folder_name = f"{current_file_name}"

    # 创建保存文件的文件夹
    os.makedirs(folder_name, exist_ok=True)

    # 生成保存文件的路径
    file_path = os.path.join(folder_name, f"{task_name}.json")

    # 将JSON数据保存到文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json_data)


def list_to_str():
    dia_list = [2, 3, 5, 8, 10, 15]
    list = []
    for i in dia_list:
        _, taskId_points = generate_circular_trajectory_json(i)
        for j in taskId_points:
            list.append(j)
    # print(list)
    return list


if __name__ == "__main__":
    # # 设置参数
    radius = 8  # 半径为10
    current_path = os.path.dirname(os.path.realpath(__file__))
    print(f"current_path:{current_path}")

    arc_length = 0.1  # 两节点之间的弧长约为0.1米
    task_name = (
        "CirclePath_Rad" + str(radius) + "m"
    )  # _'+datetime.now().strftime("%Y-%m-%d-%H%M%S")
    task_name = os.path.join(current_path, task_name)
    print(f"task_name:{task_name}")
    list_to_str()

    # # 生成圆形轨迹的JSON
    json_output, taskId_points = generate_circular_trajectory_json(radius)

    save_json_to_file(json_output, task_name)
    # print(f"taskId_points:{taskId_points}")

    # _, sdd = generate_circular_trajectory_json(3)
    # print(f"taskId_points:{sdd}")

    # 生成直线轨迹的JSON
    start = (0, 0)  # 起点
    end = (4, 0)    # 终点
    linear_json_output = generate_linear_trajectory_json(start, end)
    segments = [((0, 0), (10, 0)), ((10, 4), (0, 4)), ((0, 8), (10, 8)), ((10, 2), (0, 2)), ((0, 6), (10, 6)), ((
        10, 1), (0, 1)), ((0, 5), (10, 5)), ((10, 9), (0, 9)), ((0, 3), (10, 3)), ((10, 7), (0, 7))]

    segments = [((0, 0), (10, 0)), ((10, 4), (0, 4)), ((0, 8), (10, 8)), ((10, 2), (0, 2)), ((0, 6), (10, 6)), ((
        10, 1), (0, 1)), ((0, 5), (10, 5)), ((10, 9), (0, 9)), ((0, 3), (10, 3)), ((10, 7), (0, 7))]

    segments = [((0,  0), (6, 0)), ((6, 5), (0, 5)),
                ((0, -1), (6, -1)), ((6, 6), (0, 6)),
                ((0, -2), (6, -2)), ((6, 7), (0, 7)),
                ((0, -3), (6, -3)), ((6, 8), (0, 8)),
                ((0, -4), (6, -4)), ((6, 9), (0, 9)),
                ((0, -5), (6, -5)), ((6, 10), (0, 10)),]
    x = 3
    segments = [((0,  0), (x, 0)),  ((x, 5), (0, 5)),
                ((0, -1), (x, -1)), ((x, 6), (0, 6)),
                ((0, -2), (x, -2)), ((x, 7), (0, 7)),
                ((0, -3), (x, -3)), ((x, 8), (0, 8)),
                ((0, -4), (x, -4)), ((x, 9), (0, 9)),
                ((0, -5), (x, -5)), ((x, 10), (0, 10)),
                ((0,  0), (x, 0)),  ((x, 5), (0, 5)),
                ((0,  0), (0.1, 0)), ]

    x = 2
    segments = [((0,  0), (x, 0)),  ((x, 5-1), (0, 5-1)),
                ((0, -1+1), (x, -1+1)), ((x, 6-1),  (0,  6-1)),
                ((0, -2+1), (x, -2+1)), ((x, 7-1),  (0,  7-1)),
                ((0, -3+1), (x, -3+1)), ((x, 8-1),  (0,  8-1)),
                ((0, -4+1), (x, -4+1)), ((x, 9-1),  (0,  9-1)),
                ((0, -5+1), (x, -5+1)), ((x, 10-1), (0, 10-1)),
                ((0, -6+1), (x, -6+1)), ((x, 11-1), (0, 11-1)),
                ((0, -7+1), (x, -7+1)), ((x, 12-1), (0, 12-1)),
                ((0, -8+1), (x, -8+1)), ((x, 13-1), (0, 13-1)),
                ((0, -9+1), (x, -9+1)), ((x, 14-1), (0, 14-1)),
                ]
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

    linear_json_output = generate_linears_trajectory_json(segments)
    linear_task_name = "cirRRRRR"
    save_json_to_file(linear_json_output, linear_task_name)
    print(f"Linear trajectory saved with task name: {linear_task_name}")
