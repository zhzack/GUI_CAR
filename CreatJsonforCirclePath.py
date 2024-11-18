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


def calculate_angle(center, point):
    C_x, C_y = center
    P_x, P_y = point

    # 计算方向向量
    dx = P_x - C_x
    dy = P_y - C_y

    # 计算角度
    return math.atan2(dy, dx)


def generate_node(id, x, y, special=False, stay_time=3):
    # 生成普通节点或特殊节点
    node = {"id": id, "pos": {"x": x, "y": y}}
    if special:
        node["task"] = {
            "task_id": id,
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
        }
    return node


def generate_line_nodes(start_point, end_point, nodes=[], arc_length=0.1, add_special_nodes=False):
    direction_vector = (end_point[0] - start_point[0], end_point[1] - start_point[1])
    length = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
    unit_vector = (direction_vector[0] / length, direction_vector[1] / length)
    num_nodes = int(length / arc_length)

    for i in range(num_nodes + 1):
        x = round(start_point[0] + i * arc_length * unit_vector[0], 3)
        y = round(start_point[1] + i * arc_length * unit_vector[1], 3)

        # 生成普通节点
        node = generate_node(i + 1, x, y)

        # 如果需要添加特殊节点，检查是否是特殊位置
        if add_special_nodes and x % 1 == 0:  # 例如每隔1米添加一个特殊节点
            node = generate_node(i + 1, x, y, special=True)
        
        nodes.append(node)
    return nodes


def generate_arc_nodes(start_point, end_point, nodes=[], rotation_direction=1, arc_length=0.1, add_special_nodes=False):
    radius = calculate_radius(start_point, end_point)
    center_x = (start_point[0] + end_point[0]) / 2
    center_y = (start_point[1] + end_point[1]) / 2

    angle_start = calculate_angle((center_x, center_y), start_point)
    angle_end = calculate_angle((center_x, center_y), end_point)

    arc_length_actual = math.pi * radius  # 半圆的弧长
    num_nodes = int(arc_length_actual / arc_length)
    rotation_direction%=2
    for i in range(num_nodes + 1):
        if rotation_direction == 1:  # 顺时针
            angle = angle_start + (angle_end - angle_start) * (i / num_nodes)
        else:  # 逆时针
            angle = angle_start - (angle_end - angle_start) * (i / num_nodes)

        x = round(center_x + radius * math.cos(angle), 3)
        y = round(center_y + radius * math.sin(angle), 3)

        # 生成普通节点
        node = generate_node(len(nodes) + 1, x, y)

        # 如果需要添加特殊节点
        if add_special_nodes and i % 10 == 0:  # 例如每10个节点添加一个特殊节点
            node = generate_node(len(nodes) + 1, x, y, special=True)

        nodes.append(node)
    return nodes


def generate_linear_trajectory_json(start_point, end_point, nodes=[], arc_length=0.1, add_special_nodes=False):
    task_name = "LinearPath"
    nodes = generate_line_nodes(start_point, end_point, nodes, arc_length, add_special_nodes)
    data = {"task_name": task_name, "nodes": nodes}
    return json.dumps(data, indent=4, ensure_ascii=False)


def generate_circular_trajectory_json(radius, arc_length=0.1, special_angle=30,add_special_nodes=False):
    task_name = f"CirclePath_Rad{radius}m"
    center = (0, radius)
    circumference = 2 * math.pi * radius
    num_nodes = int(circumference / arc_length)

    nodes = []
    
    next_special_angle = special_angle
    next_special_angle_id = 0
    stay_time = 3

    for i in range(num_nodes + 2):
        theta = arc_length / radius * i
        degrees = math.degrees(theta)

        while degrees >= next_special_angle:
            special_theta = math.radians(next_special_angle)
            special_x = round(center[0] + radius * math.sin(special_theta), 3)
            special_y = round(center[1] - radius * math.cos(special_theta), 3)
            nodes.append(generate_node(i + 1 + next_special_angle_id, special_x, special_y, special=True, stay_time=stay_time))
            next_special_angle_id += 1
            next_special_angle += special_angle
            continue

        if math.degrees(theta) < 360:
            x = round(center[0] + radius * math.sin(theta), 3)
            y = round(center[1] - radius * math.cos(theta), 3)
            nodes.append(generate_node(i + 1 + next_special_angle_id, x, y))

    return json.dumps({"task_name": task_name, "nodes": nodes}, indent=4, ensure_ascii=False)

def generate_linears_trajectory_json(segments,add_special_nodes=True, arc_length=0.1):
    all_nodes = []  # 用于存储所有节点
    last_start_point = None
    last_end_point = None
    i = 1
    for start_point, end_point in segments:
        i += 1
        # 如果有前一段线段，则添加圆弧
        if last_start_point is not None and last_end_point is not None:

            all_nodes = generate_arc_nodes(
                last_end_point, start_point, all_nodes, i, arc_length,add_special_nodes)

        # 生成当前线段的节点并添加到总节点中
        all_nodes = generate_line_nodes(
            start_point, end_point, all_nodes,add_special_nodes=add_special_nodes)
        # print(len(all_nodes))

        # 更新最后的起始和结束点
        last_start_point = start_point
        last_end_point = end_point

    return json.dumps({"task_name": "PathWithArcs", "nodes": all_nodes}, ensure_ascii=False)


def save_json_to_file(json_data, task_name):
    # current_date = datetime.now().strftime("%Y-%m-%d")
    current_file_name = os.path.splitext(os.path.basename(__file__))[0]

    folder_name = f"{current_file_name}"
    os.makedirs(folder_name, exist_ok=True)

    file_path = os.path.join(folder_name, f"{task_name}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json_data)


if __name__ == "__main__":
    # 设置参数
    radius = 3  # 半径为8
    arc_length = 0.1  # 两节点之间的弧长约为0.1米
    add_special_nodes = True  # 控制是否添加特殊节点
    special_angle=30 #经过special_angle度添加特殊节点

    # 生成圆形轨迹的JSON
    json_output = generate_circular_trajectory_json(radius, arc_length,special_angle, add_special_nodes)
    task_name = f"CirclePath_Rad{radius}m"
    save_json_to_file(json_output, task_name)
    print(f"Circular trajectory saved with task name: {task_name}")

    # 生成直线轨迹的JSON
    start = (0, 0)  # 起点
    end = (10, 0)    # 终点
    linear_json_output = generate_linear_trajectory_json(start, end, arc_length=arc_length, add_special_nodes=add_special_nodes)
    linear_task_name = f"LinearPath{end[0]}"
    save_json_to_file(linear_json_output, linear_task_name)
    print(f"Linear trajectory saved with task name: {linear_task_name}")

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

    linear_json_output = generate_linears_trajectory_json(segments,add_special_nodes)
    linear_task_name = "linePath100"
    save_json_to_file(linear_json_output, linear_task_name)
    print(f"Linear trajectory saved with task name: {linear_task_name}")
