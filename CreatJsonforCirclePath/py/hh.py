import numpy as np
import matplotlib.pyplot as plt
import json

# 原始点（奇数行直线，偶数行为倒车圆弧连接）
original_points = [
    (0, 0),
    (5, 0),
    (0, 1),
    (5, 1),
    (0, 2),
    (5, 2),
    (0, 3),
    (5, 3)
]

# 参数设置
step = 0.1  # 10cm 步长
turning_radius = 0.5  # 圆弧转弯半径，单位：米

def interpolate_line(p1, p2, direction):
    vec = np.array(p2) - np.array(p1)
    length = np.linalg.norm(vec)
    steps = int(length // step)
    unit_vec = vec / length * step
    points = [np.array(p1) + i * unit_vec for i in range(steps)]
    return [{"x": float(p[0]), "y": float(p[1]), "direction": direction} for p in points]

def generate_arc(p1, p2, forward_vec1, forward_vec2, radius, direction):
    # 构造与两方向单位向量夹角为theta的圆弧
    # 通过两条向量反向延伸并求交点构造圆心
    v1 = forward_vec1 / np.linalg.norm(forward_vec1)
    v2 = forward_vec2 / np.linalg.norm(forward_vec2)
    
    # 计算夹角一半
    angle = np.arccos(np.clip(np.dot(v1, v2), -1, 1)) / 2
    if angle == 0:
        return []  # 平行无需转弯
    
    # 内角角平分线方向
    bisector = (v1 - v2)
    if np.linalg.norm(bisector) == 0:
        bisector = np.array([-v1[1], v1[0]])
    bisector /= np.linalg.norm(bisector)
    
    # 圆心在内角角平分线上，距离为 r / sin(angle)
    arc_center = np.array(p1) + bisector * radius / np.sin(angle)

    # 计算起始角和终止角
    vec_start = np.array(p1) - arc_center
    vec_end = np.array(p2) - arc_center
    angle_start = np.arctan2(vec_start[1], vec_start[0])
    angle_end = np.arctan2(vec_end[1], vec_end[0])

    # 确保是顺时针旋转（倒车）
    if angle_end > angle_start:
        angle_end -= 2 * np.pi

    arc_length = abs(angle_end - angle_start) * radius
    steps = int(arc_length // step)
    angles = np.linspace(angle_start, angle_end, steps)
    
    return [{"x": float(arc_center[0] + radius * np.cos(a)),
             "y": float(arc_center[1] + radius * np.sin(a)),
             "direction": 1} for a in angles]

# 生成路径点
path_points = []
for i in range(0, len(original_points) - 1, 2):
    p1 = original_points[i]
    p2 = original_points[i + 1]
    path_points.extend(interpolate_line(p1, p2, direction=0))

    if i + 2 < len(original_points):
        p3 = original_points[i + 2]
        forward_vec1 = np.array(p2) - np.array(p1)
        forward_vec2 = np.array(p3) - np.array(original_points[i + 2 + 1])
        arc_points = generate_arc(p2, p3, forward_vec1, forward_vec2, turning_radius, direction=1)
        path_points.extend(arc_points)

# 给每个点加 ID
for idx, pt in enumerate(path_points, 1):
    pt["id"] = idx

# 包装成最终 JSON
final_json = {
    "task_name": "PathWithArcs",
    "nodes": [{"id": pt["id"], "direction": pt["direction"], "pos": {"x": pt["x"], "y": pt["y"]}} for pt in path_points]
}

# 可视化路径
forward_pts = np.array([[pt["x"], pt["y"]] for pt in path_points if pt["direction"] == 0])
backward_pts = np.array([[pt["x"], pt["y"]] for pt in path_points if pt["direction"] == 1])

plt.figure(figsize=(10, 3))
if len(forward_pts):
    plt.plot(forward_pts[:, 0], forward_pts[:, 1], 'b-', label='Forward')
if len(backward_pts):
    plt.plot(backward_pts[:, 0], backward_pts[:, 1], 'r--', label='Backward')
plt.scatter(*zip(*original_points), color='black', zorder=5)
plt.legend()
plt.axis("equal")
plt.grid(True)
plt.title("Generated Path with Forward and Backward Arcs")

plt_path = "path_visualization.png"
plt.savefig(plt_path)
plt_path

