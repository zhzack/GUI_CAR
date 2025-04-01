from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

def merge_csv_files(csv_list, output_filename="merged_output.csv"):
        # 初始化一个空的 DataFrame
        combined_df = pd.DataFrame()
        
        # 逐个读取 CSV 文件并添加到 combined_df 中
        for csv_file in csv_list:
            df = pd.read_csv(csv_file)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        
        # 保存合并后的 DataFrame 到一个新的 CSV 文件中
        combined_df.to_csv(output_filename, index=False)
        print(f"Merged CSV saved as {output_filename}")

# @staticmethod
def process_degree(degree1, degree2, degree3):
    values = [degree1, degree2, degree3]
    sorted_values = sorted(values)
    degreeX=60
    if sorted_values == [degree3, degree1, degree2]:
        return degree1,0,1
    elif sorted_values == [degree2, degree3, degree1]:
        return degree3,120,3
    elif sorted_values == [degree1, degree2, degree3]:
        return degree2,240,2
    
    elif sorted_values == [degree1, degree3, degree2] and degree1>=-degreeX:
        return degree1,0,1
    
    elif sorted_values == [degree3, degree2, degree1] and degree1<=degreeX:    
        return degree1,0,1
    
    elif sorted_values == [degree3, degree2, degree1] and degree3>=-degreeX:
        return degree3,120,3

    elif sorted_values == [degree2, degree1, degree3] and degree3<=degreeX:
        return degree3,120,3
    
    elif sorted_values == [degree2, degree1, degree3] and degree2>=-degreeX:
        return degree2,240,2
    
    elif sorted_values == [degree1, degree3, degree2] and degree2<=degreeX:
        return degree2,240,2
    
    return degreeX,(0),0

# 只取正面的120度
def process_degree_direct_120(degree1, degree2, degree3):
    values = [degree1, degree2, degree3]
    sorted_values = sorted(values,reverse=1)#降序
    degreeX=60
    if sorted_values == [degree3, degree1, degree2]:
        return degree1,+30,1
    elif sorted_values == [degree1, degree2, degree3]:
        return degree2,150,2
    elif sorted_values == [degree2, degree3, degree1]:
        return degree3,270,3
    
    
    elif sorted_values == [degree1, degree3, degree2] and degree1<=degreeX:
        return degree1,+30,4
    
    elif sorted_values == [degree1, degree3, degree2] and degree2>=-degreeX:
        return degree2,150,5
    
    
    elif sorted_values == [degree2, degree1, degree3] and degree2<=degreeX:
        return degree2,150,6
    
    elif sorted_values == [degree2, degree1, degree3] and degree3>=-degreeX:
        return degree3,270,7
    
    
    elif sorted_values == [degree3, degree2, degree1] and degree3<=degreeX:
        return degree3,270,8
    
    elif sorted_values == [degree3, degree2, degree1] and degree1>=-degreeX:
        return degree1,390,9
    
    return degreeX,(0),0
# 正侧面60度
def process_degree_direct_60(degree1, degree2, degree3):
    values = [degree1, degree2, degree3]
    sorted_values = sorted(values,reverse=1)#降序
    
    if sorted_values == [degree3, degree1, degree2]:
        return sorted_values[1],+60,1
    
    elif sorted_values == [degree1, degree3, degree2] :
        return -sorted_values[1],60+60,2
    
    elif sorted_values == [degree1, degree2, degree3]:
        return sorted_values[1],60+60+60,3
    
    elif sorted_values == [degree2, degree1, degree3] :
        return -sorted_values[1],60+60+60+60,4
    
    elif sorted_values == [degree2, degree3, degree1]:
        return  sorted_values[1],60+60+60+60+60,5
    
    elif sorted_values == [degree3, degree2, degree1] :
        return  -sorted_values[1],60+60+60+60+60+60,6
    
    
# @staticmethod
def process_values(pdoa1, pdoa2, pdoa3):
    values = [pdoa1, pdoa2, pdoa3]
    sorted_values = sorted(values)
    pdoaX=156
    if sorted_values == [pdoa3, pdoa1, pdoa2]:
        return pdoa1,0
    elif sorted_values == [pdoa2, pdoa3, pdoa1]:
        return pdoa3,120
    elif sorted_values == [pdoa1, pdoa2, pdoa3]:
        return pdoa2,240
    
    elif sorted_values == [pdoa1, pdoa3, pdoa2] and pdoa1>=-pdoaX:
        return pdoa1,0
    
    elif sorted_values == [pdoa3, pdoa2, pdoa1] and pdoa1<=pdoaX:
        return pdoa1,0
    
    elif sorted_values == [pdoa3, pdoa2, pdoa1] and pdoa3>=-pdoaX:
        return pdoa3,120
    
    elif sorted_values == [pdoa2, pdoa1, pdoa3] and pdoa3<=pdoaX:
        return pdoa3,120
    
    elif sorted_values == [pdoa2, pdoa1, pdoa3] and pdoa2>=-pdoaX:
        return pdoa2,240
    
    elif sorted_values == [pdoa1, pdoa3, pdoa2] and pdoa2<=pdoaX:
        return pdoa2,240
    
    return pdoaX,(0)


# 实时将pdoa转为角度0-360
# @staticmethod
def process_pdoaToAng(pdoa_first, pdoa_second, pdoa_third):
    def limit_value(value):
            if value > 180:
                return 1
            elif value < -180:
                return -1
            else:
                return value/180

    pdoa_first = limit_value(pdoa_first)
    pdoa_second = limit_value(pdoa_second)
    pdoa_third = limit_value(pdoa_third)
    
    # Custom3DPlot.process_values(pdoa_first,pdoa_second,pdoa_third)
    pdoa_ressult,pdoa_offset=process_values(pdoa_first, pdoa_third,pdoa_second)
    
    # print(f"np.arcsin(pdoa_first):{np.arcsin(pdoa_first)}")
    # print(f"np.arcsin(pdoa_second):{np.arcsin(pdoa_second)}")
    # print(f"np.arcsin(pdoa_third):{np.arcsin(pdoa_third)}")
    
    
    arcsin_degrees1=np.degrees(np.arcsin(pdoa_first))
    arcsin_degrees2=np.degrees(np.arcsin(pdoa_second))
    arcsin_degrees3=np.degrees(np.arcsin(pdoa_third))
    # print(f"arcsin_degrees1:{arcsin_degrees1}")
    # print(f"arcsin_degrees2:{arcsin_degrees2}")
    # print(f"arcsin_degrees3:{arcsin_degrees3}")
    
    # degree_result,degree_offset,x=process_degree_direct_60(arcsin_degrees1,arcsin_degrees2,arcsin_degrees3)
    degree_result,degree_offset,x=process_degree_direct_120(arcsin_degrees1,arcsin_degrees2,arcsin_degrees3)

    # print(degree_result,degree_offset+120)
    return (degree_result+degree_offset)%360,x,degree_offset,degree_result,arcsin_degrees1,arcsin_degrees2,arcsin_degrees3

def ll_data(file_name):
    fm = file_name
    df = pd.read_csv(fm)

    x = df['sessionNumber']
    y_distance = df['Distance']
    y_azimuth = df['AoAAzimuth']
    y_elevation = df['AoAElevation']
    y_PdoaFirst = df['PdoaFirst']
    y_PdoaSecond = df['PdoaSecond']
    y_PdoaThird = df['PdoaThird']
    
    print("PdoaFirst:", df['PdoaFirst'].mean())
    print("PdoaSecond:", df['PdoaSecond'].mean())
    print("PdoaThird:", df['PdoaThird'].mean())
    
    print("AoAAzimuth:", df['AoAAzimuth'].mean())
    print("AoAElevation:", df['AoAElevation'].mean())
    print("Distance:", df['Distance'].mean())

    plt.figure(figsize=(10, 6))
    plt.plot(x, y_distance, label='Distance')
    plt.plot(x, y_azimuth, label='AoAAzimuth')
    plt.plot(x, y_PdoaFirst, label='PdoaFirst')
    plt.plot(x, y_PdoaSecond, label='PdoaSecond')
    plt.plot(x, y_PdoaThird, label='PdoaThird')
    
    plt.xlabel('sessionNumber')
    plt.ylabel('Value')
    plt.title(fm)
    plt.legend()
    plt.grid(True)
    plt.show()

# 每列数据的平均值中位数标准差计算
def data_ca(filename):
    df = pd.read_csv(filename)
    
    # 要统计的列名称
    columns_to_analyze = ['Distance', 'AoAAzimuth', 'AoAElevation', 'PdoaFirst', 'PdoaSecond', 'PdoaThird']
    columns_to_analyze = ['Distance', 'AoAAzimuth', 'PdoaFirst', 'PdoaSecond', 'PdoaThird','AoAAzimuth1']

    # 创建一个空的字典，用于存储统计结果
    stats = {
        '列名': [],
        '均值': [],
        '中位数': [],
        '方差': [],
        '标准差': [],
        '最大值': [],
        '最小值': []
    }
    # 计算每列的统计信息
    for column in columns_to_analyze:
        stats['列名'].append(column)
        stats['均值'].append(df[column].mean())
        stats['中位数'].append(df[column].median())
        stats['方差'].append(df[column].var())
        stats['标准差'].append(df[column].std())
        stats['最大值'].append(df[column].max())
        stats['最小值'].append(df[column].min())
    # 获取特定列的名称
    column_name = 'sessionNumber'

    # 获取第一行的值
    first_row_value = df[column_name].iloc[0]

    # 获取最后一行的值
    last_row_value = df[column_name].iloc[-1]

    # 获取行数
    num_rows = df.shape[0]

    # 计算最后一行的值减去第一行的值与行数的比值（以百分比展示）
    percentage_change = (num_rows/(last_row_value - first_row_value) ) * 100
    
    # process_pdoaToAng

    # 将统计信息转换为 DataFrame
    stats_df = pd.DataFrame(stats)
    stats_df['列名'] = stats_df['列名'].astype(str)
    
    azimuth = stats_df['均值'][1]
    pdoa1_avg = stats_df['均值'][2]
    pdoa2_avg = stats_df['均值'][3]
    pdoa3_avg = stats_df['均值'][4]
    azimuth1 = stats_df['均值'][5]
    
    for column in columns_to_analyze:
        # print(f"{column}的均值为：{stats_df['均值'][columns_to_analyze.index(column)]}")
        pass
    
    avg_ang ,x,offSet,degree_result,arcsin_degrees1,arcsin_degrees2,arcsin_degrees3= process_pdoaToAng(pdoa1_avg,pdoa2_avg,pdoa3_avg)
    print(f"pdoa1_avg:{pdoa1_avg},pdoa2_avg:{pdoa2_avg},pdoa3_avg:{pdoa3_avg},x:{x},offSet:{offSet},avg_ang:{avg_ang},degree_result:{degree_result},arcsin_degrees1:{arcsin_degrees1},arcsin_degrees2:{arcsin_degrees2},arcsin_degrees3:{arcsin_degrees3}")
    
    # print(pdoa1_avg,pdoa2_avg,pdoa3_avg)
    
    # print(stats_df)
    # print(f"last_row,{last_row_value},first_row,{first_row_value},num_rows,{num_rows},percentage,{percentage_change}")
