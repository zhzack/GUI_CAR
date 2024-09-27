import math

def calculate_arc_parameters(segment1, segment2, radius):
    # 提取线段的起始点和结束点
    p1, p2 = segment1
    p3, p4 = segment2

    # 计算中点作为圆心
    center_x = (p2[0] + p3[0]) / 2
    center_y = (p2[1] + p3[1]) / 2

    # 计算起始角度
    start_angle = math.atan2(p2[1] - center_y, p2[0] - center_x)
    # 计算结束角度
    end_angle = math.atan2(p3[1] - center_y, p3[0] - center_x)

    # 判断转弯方向
    direction_vector = (p3[0] - p2[0], p3[1] - p2[1])
    turn_direction = 'left' if direction_vector[1] > 0 else 'right'

    return {
        "center": (center_x, center_y),
        "radius": radius,
        "start_angle": start_angle,
        "end_angle": end_angle,
        "direction": turn_direction
    }

# 示例
segment1 = ((0, 0), (4, 0))  # 第一条线段
segment2 = ((4, 0), (4, 5))  # 第二条线段
radius = 2.0  # 小车的转弯半径

arc_parameters = calculate_arc_parameters(segment1, segment2, radius)
print(arc_parameters)
