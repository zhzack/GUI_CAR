def parse_sensor_data(data_str):
    # 1. 按空格分隔每个传感器的数据块
    sensor_data_list = data_str.split()

    # 2. 创建一个字典来存储传感器数据
    sensors = {}

    # 3. 遍历每个传感器数据块
    for sensor_data in sensor_data_list:
        # 4. 按逗号分隔传感器的名称和数值
        sensor_parts = sensor_data.split(',')
        
        # 5. 获取传感器名称
        sensor_name = sensor_parts[0]
        
        # 6. 获取传感器数值，将其转换为整数
        values = list(map(int, sensor_parts[1:]))
        
        # 7. 存储到字典中
        sensors[sensor_name] = values

    return sensors

# 示例数据
data = "car,0,0,1 UWB1,0,0,1 UWB2,0,0,1 BLE,2,0,1"

# 解析数据
parsed_data = parse_sensor_data(data)

# 打印结果
print(parsed_data)
