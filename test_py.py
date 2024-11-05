import pandas as pd
import matplotlib.pyplot as plt
import os

current_path = os.path.dirname(os.path.realpath(__file__))
path = '不同距离绕圈'
csv_file_path = os.path.join(
    current_path, 'show_data_path', path, '绕圈10301435两移远新板子.csv')
# 读取CSV文件
df = pd.read_csv(csv_file_path)

# 选择要处理的三列，假设这三列是列名为 'col1', 'col2', 'col3'
str_pdoa20 = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa20'
str_pdoa12 = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa12'
str_pdoa01 = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa01'
columns_to_process = [str_pdoa20,str_pdoa12,str_pdoa01]

# 用于存储上一行有效的数据
last_valid_data = {col: None for col in columns_to_process}

# 遍历前500行（从第二行开始）
for i in range(1, len(df)):
    for col in columns_to_process:
        current_value = df[col].iloc[i]
        
        # 检查当前行是否有有效数据，如果没有，则跳过
        if pd.notna(current_value):
            # 如果上一行有有效数据
            if last_valid_data[col] is not None:
                # 判断是否满足差值条件
                if abs(current_value - last_valid_data[col]) >= 230:
                    if last_valid_data[col] < current_value:
                        # 当前行减去差值
                        df[col].iloc[i] -= abs(current_value - last_valid_data[col])
                    else:
                        # 当前行加上差值
                        df[col].iloc[i] += abs(current_value - last_valid_data[col])
            
            # 更新上一行有效数据
            last_valid_data[col] = df[col].iloc[i]


# 绘制折线图
plt.figure(figsize=(10, 6))
for col in columns_to_process:
    plt.plot(df.index, df[col], label=col)

# 设置图形标题和标签
plt.title('Processed Data')
plt.xlabel('Index')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
plt.show()
