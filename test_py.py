import numpy as np
import matplotlib.pyplot as plt

# 已知的两条直线的点
line1 = [(0, 0), (3, 0)]  # 第一条直线，水平线
line2 = [(0, 3), (4, 5)]  # 第二条直线

# 提取点
p1, p2 = line1
p3, p4 = line2



# 计算连接线段的中心点
midpoint1 = ((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2)  # 连接线段的中心点
midpoint2 = ((p2[0] + p4[0]) / 2, (p2[1] + p4[1]) / 2)  # 连接线段的中心点

# 计算连接线段的中点
connection_center = ((midpoint1[0] + midpoint2[0]) / 2, (midpoint1[1] + midpoint2[1]) / 2)

# 圆的半径
circle_radius = 2

# 找到与（0, 3）到（0, 0）相切的圆心
# 该圆心在连接线段上，并与线段的距离等于半径
# 直线方程为 x = 0 (从(0,0)到(0,3))

# 圆心在连接线段上的点
circle_center = (connection_center[0], connection_center[1] + circle_radius)  # 向上移动半径

# 绘制圆
theta = np.linspace(0, 2 * np.pi, 100)
x_circle = circle_center[0] + circle_radius * np.cos(theta)
y_circle = circle_center[1] + circle_radius * np.sin(theta)

# 设置绘图范围
x_values = np.linspace(-1, 5, 100)

# 计算直线的y值
y_line1 = np.zeros_like(x_values)  # 第一条直线：y = 0
y_line2 = (1/2) * x_values + 3  # 第二条直线

# 绘制两条直线
plt.figure(figsize=(10, 6))
plt.plot(x_values, y_line1, label='Line 1: y = 0', color='red')
plt.plot(x_values, y_line2, label='Line 2: y = (1/2)x + 3', color='green')

# 绘制连接顶点的线段
plt.plot([p1[0], p3[0]], [p1[1], p3[1]], color='orange', linestyle='--', label='Connection 1')
plt.plot([p2[0], p4[0]], [p2[1], p4[1]], color='purple', linestyle='--', label='Connection 2')

# 绘制连接中心点的线段
plt.plot([midpoint1[0], midpoint2[0]], [midpoint1[1], midpoint2[1]], color='blue', linestyle='-.', label='Midpoint Connection')


# 绘制圆
plt.plot(x_circle, y_circle, color='orange', label='Circle (radius = 2)', linestyle='-')

# 设置坐标轴范围
plt.xlim(-1, 5)
plt.ylim(-1, 6)
plt.axhline(0, color='black', linewidth=0.5, ls='--')
plt.axvline(0, color='black', linewidth=0.5, ls='--')
plt.gca().set_aspect('equal', adjustable='box')
plt.legend()
plt.xlabel('X轴')
plt.ylabel('Y轴')
plt.title('连接线段及其相切的圆')
plt.grid()
plt.show()
