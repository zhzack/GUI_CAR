import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from calculate import process_pdoaToAng


def plot_multiple_curves(data_list, title, xlabel, ylabel):
    """
    绘制多个曲线
    :param data_list: 包含字典的数组，每个字典包含 'name' 和 'values' 键
                      例如 [{'name': 'Curve1', 'values': [1, 2, 3]},
                          {'name': 'Curve2', 'values': [4, 5, 6]}]
    :param title: 图像标题
    :param xlabel: X轴标签
    :param ylabel: Y轴标签
    """
    plt.figure(figsize=(12, 8))
    for data in data_list:
        plt.plot(data['values'], marker='o', label=data['name'])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()


def plot_path_comparison(x_coords, y_coords, carsts_x, carsts_y):
    """
    绘制路径对比图像
    :param x_coords: 计算的 X 坐标列表
    :param y_coords: 计算的 Y 坐标列表
    :param carsts_x: CarSts 的 X 坐标列表
    :param carsts_y: CarSts 的 Y 坐标列表
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x_coords, y_coords, marker='o', label='Computed Path')
    plt.scatter(carsts_x, carsts_y, color='red', label='CarSts Path')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title('Path Comparison')
    plt.legend()
    plt.grid()
    plt.show()


def get_col_name(short_name: str) -> str:
    """
    将 '模块名.字段名' 转换为完整列名字符串。

    例：
        输入: 'CAR_UWB_Copy_1.uwb_fob_location_distance'
        输出: 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB_Copy_1::uwb_fob_location_distance'
    """
    common_prefix = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::'

    if '.' not in short_name:
        raise ValueError("输入格式应为 '模块名.字段名'")

    module, field = short_name.split('.', 1)
    return f'{common_prefix}{module}::{field}'


def get_cols_name(module_name: str, fields: list) -> dict:
    """
    批量生成完整列名，返回一个字段名到完整列名的映射字典。

    参数:
        module_name: 模块名，如 'CAR_UWB_Copy_1'
        fields: 字段名列表，如 ['uwb_fob_location_distance', 'uwb_fob_location_x']

    返回:
        {
            'uwb_fob_location_distance': 'NDLB_VKM...::CAR_UWB_Copy_1::uwb_fob_location_distance',
            ...
        }
    """
    common_prefix = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::'
    return {
        field: f"{common_prefix}{module_name}::{field}" for field in fields
    }


def process_csv(file_path):
    # 读取 CSV 文件
    data = pd.read_csv(file_path)

    uwb1 = {get_col_name('CAR_UWB.pdoa20_col')}
    col_dict = get_cols_name('CAR_UWB_Copy_1', fields)

    print(col_dict)

    # 提取所需列
    pdoa20_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa20'
    pdoa12_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa12'
    pdoa01_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_pdoa01'
    uwb_fob_location_distance_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_distance'
    uwb_fob_location_index_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_index'
    uwb_fob_location_x_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_x'
    uwb_fob_location_y_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB::uwb_fob_location_y'

    # # 提取所需列
    pdoa20_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB_Copy_1::uwb_fob_location_pdoa20'
    pdoa12_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB_Copy_1::uwb_fob_location_pdoa12'
    pdoa01_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB_Copy_1::uwb_fob_location_pdoa01'
    uwb_fob_location_distance_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB_Copy_1::uwb_fob_location_distance'
    uwb_fob_location_index_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB_Copy_1::uwb_fob_location_index'
    uwb_fob_location_x_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB_Copy_1::uwb_fob_location_x'
    uwb_fob_location_y_col = 'NDLB_VKM_PrivateCAN_V1.0.7_0x78_V1::CAR_UWB_Copy_1::uwb_fob_location_y'

    carsts_x_col = get_col_name('CarSts.Carsts_X')
    carsts_y_col = get_col_name('CarSts.Carsts_Y')

    if all(col in data.columns for col in [pdoa20_col, pdoa12_col, pdoa01_col, uwb_fob_location_distance_col, carsts_x_col, carsts_y_col]):
        x_coords = []
        y_coords = []
        prev_x = None
        prev_y = None
        pdoa20_values = []
        pdoa12_values = []
        pdoa01_values = []
        fob_x_values = []
        fob_y_values = []
        angles = []
        distances = []
        index_values = []  # 用于存储 uwb_fob_location_index 的值

        for _, row in data.iterrows():
            pdoa20 = row[pdoa20_col]
            pdoa12 = row[pdoa12_col]
            pdoa01 = row[pdoa01_col]
            distance = row[uwb_fob_location_distance_col]
            fob_x = row[uwb_fob_location_x_col]
            fob_y = row[uwb_fob_location_y_col]

            carsts_x = (row[carsts_x_col])
            carsts_y = (row[carsts_y_col])

            # 调用 process_pdoaToAng 计算结果
            angle, x, offset, degree_result, arcsin_degrees1, arcsin_degrees2, arcsin_degrees3 = process_pdoaToAng(
                # pdoa20, pdoa12, pdoa01
                pdoa01, pdoa20, pdoa12
            )

            # 计算 xy 坐标
            computed_x = distance * np.cos(np.radians(angle))
            computed_y = distance * np.sin(np.radians(angle))

            # # 对比当前坐标与上一次的 Carsts_X 和 Carsts_Y
            # if prev_x is not None and prev_y is not None:
            #     print(f"与上一次对比: ΔX={computed_x - prev_x}, ΔY={computed_y - prev_y}")

            prev_x = carsts_x
            prev_y = carsts_y

            x_coords.append(computed_x)
            y_coords.append(computed_y)

            # 记录 PDOA 值、角度和距离
            pdoa20_values.append(pdoa20)
            pdoa12_values.append(pdoa12)
            pdoa01_values.append(pdoa01)
            fob_x_values.append(fob_x)
            fob_y_values.append(fob_y)

            angles.append(angle)
            distances.append(distance)
            index_value = row[uwb_fob_location_index_col]
            index_values.append(index_value)  # 记录 index 值

        # # 调用绘制路径对比图像的函数
        plot_path_comparison(
            x_coords,
            y_coords,
            # fob_x,
            # fob_y,
            data[carsts_x_col] / 10,  # 将值除以 100
            data[carsts_y_col] / 10   # 将值除以 100
        )

        # 使用通用函数绘制角度、距离、PDOA 和索引曲线
        plot_multiple_curves(
            [
                # {'name': 'Angle Change', 'values': angles},
                {'name': 'Distance Change', 'values': distances}
            ],
            title='Angle and Distance Change Curves',
            xlabel='Index',
            ylabel='Value'
        )

        plot_multiple_curves(
            [
                {'name': 'PDOA20', 'values': pdoa20_values},
                {'name': 'PDOA12', 'values': pdoa12_values},
                {'name': 'PDOA01', 'values': pdoa01_values},
                {'name': 'Computed Angle', 'values': angles}
            ],
            title='PDOA Values and Computed Angle Curve',
            xlabel='Index',
            ylabel='Value'
        )

        # plot_multiple_curves(
        #     [
        #         {'name': 'UWB FOB Location Index Change', 'values': index_values}
        #     ],
        #     title='UWB FOB Location Index Change Curve',
        #     xlabel='Index',
        #     ylabel='UWB FOB Location Index'
        # )
    else:
        print("CSV 文件中缺少必要的列，请检查文件格式。")


if __name__ == "__main__":
    fields = [
        'uwb_fob_location_pdoa20',
        'uwb_fob_location_pdoa12',
        'uwb_fob_location_pdoa01',
        'uwb_fob_location_distance',
        'uwb_fob_location_index',
        'uwb_fob_location_x',
        'uwb_fob_location_y'
    ]
    # 假设数据已加载到 DataFrame 中
    current_path = os.path.dirname(os.path.realpath(__file__))
    path = '2025年4月11日'
    file_name = '绕圈不停顿-前146后145-i高度77-距离69.csv'
    file_name = '绕圈-前146后145-i高度77-距离69-前期145掉落看稳定后数据.csv'
    file_name = '145新移远146上一次移远tag高度143两锚点高度163-距离65.csv'

    path = '2025年4月11日'
    file_name = '绕圈不停顿-前145后146-i高度77-距离85.csv'
    file_name = '绕圈不停顿-前145后146-i高度77-距离93.csv'
    file_name = '绕圈不停顿-前145后146-i高度77-距离93-2.csv'
    file_name = '绕圈不停顿-前145后146-i高度77-距离105.csv'
    file_name = '绕圈停顿-前145后146-i高度77-距离104.csv'

    path = '2025年4月21日'
    file_name = 'data_142709_01_94.csv'
    file_name = 'data_143758_12_96.csv'
    file_name = 'data_135959_02_99.csv'

    if path != '':
        current_path = os.path.join(current_path, path, file_name)
    else:
        current_path = os.path.join(current_path, file_name)

    # 处理 CSV 文件
    process_csv(current_path)
