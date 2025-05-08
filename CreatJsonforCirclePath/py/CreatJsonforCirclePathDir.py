import json
import math
import matplotlib.pyplot as plt


def generate_node(id, x, y, special=False, stay_time=3, direction=0):
    # 生成普通节点或特殊节点
    node = {"id": id,  "direction": direction, "pos": {"x": x, "y": y}}
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


def generate_line_nodes(start_point, end_point, nodes=[], dir=0, arc_length=0.1, add_special_nodes=False):
    direction_vector = (end_point[0] - start_point[0],
                        end_point[1] - start_point[1])
    print(direction_vector)
    length = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
    unit_vector = (direction_vector[0] / length, direction_vector[1] / length)
    num_nodes = int(length / arc_length)

    for i in range(num_nodes + 1):
        x = round(start_point[0] + i * arc_length * unit_vector[0], 3)
        y = round(start_point[1] + i * arc_length * unit_vector[1], 3)

        # 生成普通节点
        node = generate_node(i + 1, x, y, direction=dir)

        # 如果需要添加特殊节点，检查是否是特殊位置
        if add_special_nodes and x % 1 == 0:  # 例如每隔1米添加一个特殊节点
            node = generate_node(i + 1, x, y, special=True, direction=dir)

        nodes.append(node)
    return nodes


def generate_direction_nodes(points):
    nodes = []

    for i in range(len(points)):
        if i + 1 < len(points):
            nodes = generate_line_nodes(
                points[i], points[i + 1], nodes, dir=i % 2, arc_length=0.1, add_special_nodes=True)

    return {
        "task_name": "PathWithArcs",
        "nodes": nodes
    }


def generate_arc_points(start_x, start_y, radius, angle_deg, step_length=0.1, clockwise=True):
    """
    根据给定弧度，按照固定步长生成圆弧上的点。
    参数：
      start_x, start_y: 弧线起点坐标
      radius: 圆弧半径
      angle_deg: 圆弧弧度（单位：度）
      step_length: 节点间的弧长（米），默认 0.1 米
      clockwise: True 表示后退（圆弧为顺时针方向），False 表示逆时针
    返回：
      点列表，每个点为 (x, y)
    """
    points = []
    angle_rad = math.radians(angle_deg)  # 总圆弧角度（弧度）
    arc_total_length = radius * angle_rad  # 圆弧总长
    steps = int(arc_total_length / step_length)
    if steps < 1:
        steps = 1
    delta_angle = angle_rad / steps
    sign = -1 if clockwise else 1

    # 假设圆心位置在起点正上方（或正下方，根据 clockwise 参数）
    # 这里设定圆心相对起点的偏移：当为顺时针时，圆心在起点正上方
    cx = start_x
    cy = start_y + (radius if clockwise else -radius)

    # 设定起始角度：确定起点在圆上对应的角度
    # 当 clockwise=True 时，起点对应角度为 -pi/2，相对于圆心的位置
    start_angle = -math.pi/2 if clockwise else math.pi/2

    for i in range(steps + 1):
        theta = start_angle + sign * delta_angle * i
        x = cx + radius * math.cos(theta)
        y = cy + radius * math.sin(theta)
        points.append((x, y))
    return points


def generate_path_with_direction(step_length=0.1):
    nodes = []
    current_x = 0.0
    current_y = 0.0
    point_id = 1
    forward_distance = 10.0  # 每段正向直线 10 米
    arc_angle = 10           # 每个后退圆弧转 10 度

    # 计算用于圆弧的半径，满足弧长 = forward_distance，对应 arc_angle
    # arc_length = radius * angle_rad  -->  radius = forward_distance / angle_rad
    # radius = forward_distance / math.radians(arc_angle)
    theta = math.radians(arc_angle)
    radius = forward_distance / (2 * math.sin(theta / 2))

    # 前进（direction=0）和后退（direction=1）的交替，生成例如3次循环
    cycles = 3
    for _ in range(cycles):
        # 正向直线部分：前进 10 米，步长为 step_length (0.1 m)
        forward_steps = int(forward_distance / step_length)
        for i in range(forward_steps + 1):
            x = current_x + i * step_length
            y = current_y
            nodes.append({
                "id": point_id,
                "direction": 0,  # 0 表示前进
                "pos": {"x": round(x, 3), "y": round(y, 3)}
            })
            point_id += 1
        # 更新当前位置到直线段终点
        current_x += forward_distance

        # 后退圆弧部分：圆弧长度也为 forward_distance
        # 这里使用 generate_arc_points，以固定节点间距为 step_length
        arc_points = generate_arc_points(
            current_x, current_y, radius, arc_angle, step_length, clockwise=True)
        for (x, y) in arc_points:
            nodes.append({
                "id": point_id,
                "direction": 1,  # 1 表示后退
                "pos": {"x": round(x, 3), "y": round(y, 3)}
            })
            point_id += 1

        # 更新当前位置为圆弧末点
        current_x, current_y = arc_points[-1]

    # 返回整体任务数据
    return {
        "task_name": "PathWithArcs",
        "nodes": nodes
    }


def save_path_json(data, filename="path_with_arcs.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def visualize_path(data):
    nodes = data["nodes"]
    x_vals = [node["pos"]["x"] for node in nodes]
    y_vals = [node["pos"]["y"] for node in nodes]
    directions = [node["direction"] for node in nodes]

    plt.figure(figsize=(10, 6))
    # 绘制每个点，正向用蓝色，后退用红色
    for x, y, d in zip(x_vals, y_vals, directions):
        color = 'blue' if d == 0 else 'red'
        plt.plot(x, y, 'o', color=color)
    plt.plot(x_vals, y_vals, linestyle='--', color='gray', linewidth=0.8)
    plt.title("Vehicle Path with 10cm Inter-Point Spacing")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.grid(True)
    plt.axis('equal')
    plt.show()


original_points = [
    (0, 0),
    (20, 0),
    (0, 1),
    (20, 1),
    (0, 2),
    (20, 2),
    (0, 3),
    (20, 3)
]
data = generate_direction_nodes(original_points)

# 生成任务数据、保存 JSON 文件，并可视化
# data = generate_path_with_direction(step_length=0.1)
save_path_json(data)
visualize_path(data)
