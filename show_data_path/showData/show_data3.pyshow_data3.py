import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import os

# 假设数据已加载到 DataFrame 中
current_path = os.path.dirname(os.path.realpath(__file__))
path = '2025年1月3日'
file_name = '1126SroundVehicle_+X276_+Y0.csv'
# str_uwb_distance='NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_distance'
# str_Carsts_X='NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CarSts::Carsts_X'
# str_Carsts_Y='NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CarSts::Carsts_Y'

str_uwb_distance = 'UWB_Simple::Anchor5UwbTx::Dis_5'
str_Carsts_X = 'UWB_Simple::CarSts::Carsts_X'
str_Carsts_Y = 'UWB_Simple::CarSts::Carsts_Y'
path = ''
file_name = '第一次大采集车外.csv'
if path != '':
    current_path = os.path.join(current_path, path, file_name)
else:
    current_path = os.path.join(current_path, file_name)
data = pd.read_csv(current_path)



# 确定 uwb_fob_location_distance 的最大和最小值
min_value = data[str_uwb_distance].min()
max_value = data[str_uwb_distance].max()

# 创建归一化对象
norm = Normalize(vmin=min_value, vmax=max_value)
cmap = plt.cm.viridis

# 创建图形和坐标轴
fig, ax = plt.subplots()
x = data[str_Carsts_X]
y = data[str_Carsts_Y]
plt.scatter(x, y, c=(1, 0, 0, 1), s=1)


color = (0, 0, 0, 0)  # 透明色
x = 0
y = 0
# 遍历每一行数据，逐个添加坐标点
for index, row in data.iterrows():
    uwb_distance = row[str_uwb_distance]
    x1 = row[str_Carsts_X]
    y1 = row[str_Carsts_Y]
    if pd.notna(x1) and pd.notna(y1):
        x = x1
        y = y1
    if pd.notna(uwb_distance) and uwb_distance > 0:  # 检查是否有值并大于0
        color = cmap(norm(uwb_distance))
        ax.plot(x, y, 'o', color=color, alpha=1)  # 'o' 表示圆点，alpha 可调


# 创建颜色条，仅显示实际数据范围
sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])  # 空数组，以激活颜色条
cbar = plt.colorbar(sm, ax=ax)  # 指定颜色条要附加的坐标轴

# 设置标签和标题
ax.set_xlabel('str_Carsts_X')
ax.set_ylabel('str_Carsts_Y')
ax.set_title(f'point color : {str_uwb_distance}\n file name :{file_name}')

# 显示图表
plt.show()
