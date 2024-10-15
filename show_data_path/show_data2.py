import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# 假设数据已加载到 DataFrame 中
data = pd.read_csv('第一次大采集车外.csv')

# 确定 uwb_fob_location_distance 的最大和最小值
min_value = 0#data['uwb_fob_location_distance'].min()
max_value = 0#data['uwb_fob_location_distance'].max()

# 创建归一化对象
norm = Normalize(vmin=min_value, vmax=max_value)
cmap = plt.cm.viridis

# 创建图形和坐标轴
fig, ax = plt.subplots()
# x = data['Carsts_X']
# y = data['Carsts_Y']
str_car_x="UWB_Simple::CarSts::Carsts_X"
str_car_y="UWB_Simple::CarSts::Carsts_Y"
x = data[str_car_x]
y = data[str_car_y]
plt.scatter(x, y, c=(1, 0, 0, 1), s=1)


color = (0, 0, 0, 0)  # 透明色
x = 0
y = 0
# 遍历每一行数据，逐个添加坐标点
for index, row in data.iterrows():
    # uwb_distance = row['uwb_fob_location_distance']
    x1 = row[str_car_x]
    y1 = row[str_car_y]
    if pd.notna(x1) and pd.notna(y1):
        x = x1
        y = y1
    # if pd.notna(uwb_distance) and uwb_distance > 0:  # 检查是否有值并大于0
    #     color = cmap(norm(uwb_distance))
    #     ax.plot(x, y, 'o', color=color, alpha=1)  # 'o' 表示圆点，alpha 可调


# 创建颜色条，仅显示实际数据范围
sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])  # 空数组，以激活颜色条
cbar = plt.colorbar(sm, ax=ax)  # 指定颜色条要附加的坐标轴

# 设置标签和标题
ax.set_xlabel(str_car_x)
ax.set_ylabel(str_car_y)
ax.set_title('坐标点颜色表示 uwb_fob_location_distance')

# 显示图表
plt.show()
