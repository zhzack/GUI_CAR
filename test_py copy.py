import math

def calculate_angle_and_direction(x1, y1, x2, y2, x3, y3, x4, y4):
    # 计算向量 AB 和 CD
    AB_x = x2 - x1
    AB_y = y2 - y1
    CD_x = x4 - x3
    CD_y = y4 - y3

    # 计算向量 AB 和 CD 的点积
    dot_product = AB_x * CD_x + AB_y * CD_y

    # 计算向量 AB 和 CD 的模长
    AB_magnitude = math.sqrt(AB_x**2 + AB_y**2)
    CD_magnitude = math.sqrt(CD_x**2 + CD_y**2)

    # 计算夹角的余弦值
    cos_theta = dot_product / (AB_magnitude * CD_magnitude)

    # 计算夹角（以弧度表示）
    theta_rad = math.acos(cos_theta)

    # 将弧度转换为角度
    theta_deg = math.degrees(theta_rad)

    # 计算叉积来判断顺时针还是逆时针
    cross_product = AB_x * CD_y - AB_y * CD_x

    # 判断方向
    if cross_product > 0:
        direction = "逆时针"
    elif cross_product < 0:
        direction = "顺时针"
    else:
        # 叉积为零时，表示直线平行，仍然返回方向
        direction = "平行，方向不可判定"

    return theta_deg, direction

# 示例调用
x1, y1 = 1, -1  # 点 A
x2, y2 = 1, 5  # 点 B
x3, y3 = 5, 5  # 点 C
x4, y4 = 6, -1  # 点 D
# x3, y3 = -5, 5  # 点 C
# x4, y4 = -5, -1  # 点 D

angle, direction = calculate_angle_and_direction(x1, y1, x2, y2, x3, y3, x4, y4)
print(f"两条直线的夹角是: {angle:.2f}°")
print(f"CD 在 AB 的方向是: {direction}")
