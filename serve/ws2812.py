import math


class Ws2812:
    def __init__(self, serial_manager):
        self.serial_manager = serial_manager
        self.leds_per_strip = 144
        self.num_strips = 15
        self.led_index_offset = 144*(-3)

        self.led_num = self.leds_per_strip*self.num_strips
        self.points = []  # 不规则轨迹的点
        self.leds_per_meter = 144  # 每米的灯数
        self.lights = None  # 预计算灯的位置和角度
        self.set_points_path([])

    def set_points_path(self, points):
        # self.points = points
        x=10
        
        self.points = [(125, 250+x), (125+x, -250), (-125, -250-x),
                       (-125-x, 250), (125, 250+x)]
        self.lights = self.distribute_lights()  # 预计算灯的位置和角度

    def calculate_segment_length(self, start, end):
        """计算两个点之间的距离"""
        return math.hypot(end[0] - start[0], end[1] - start[1])

    def distribute_lights(self):
        """根据轨迹点计算灯的位置，并计算每个灯的角度"""
        lights = []
        total_length = 0  # 轨迹总长度
        segment_lengths = []

        # 计算每段的长度并记录
        for i in range(len(self.points) - 1):
            start = self.points[i]
            end = self.points[i + 1]
            segment_length = self.calculate_segment_length(start, end)
            segment_lengths.append(segment_length)
            total_length += segment_length
        print("总长度:", total_length)

        # 总灯数
        total_leds = int(self.leds_per_meter * total_length/100)  # 计算总的灯数
        print("总灯数:", total_leds)

        # 灯的间隔
        light_spacing = total_length / (total_leds - 1)  # 每个灯之间的间隔
        print("每个灯之间的间隔:", light_spacing)

        current_length = 0  # 当前累积的长度
        for i in range(len(self.points) - 1):
            start = self.points[i]
            end = self.points[i + 1]
            segment_length = segment_lengths[i]

            # 计算当前轨迹段的灯的数量
            while current_length <= segment_length:
                t = current_length / segment_length
                x = start[0] + t * (end[0] - start[0])
                y = start[1] + t * (end[1] - start[1])

                # 计算灯的角度
                dx = x
                dy = y
                angle = math.atan2(dy, dx)  # 计算弧度
                angle_deg = math.degrees(angle)  # 转换为角度
                if angle_deg < 0:
                    angle_deg += 360  # 确保角度在 0 到 360 之间

                lights.append((x, y, angle_deg))

                current_length += light_spacing

            current_length -= segment_length  # 移动到下一个轨迹段

        print("灯的数量:", len(lights))
        return lights

    def find_nearest_led(self, angle):
        """根据角度找到最接近的灯的ID"""
        min_distance = float('inf')
        nearest_led_id = -1

        for i, (x, y, light_angle) in enumerate(self.lights):
            distance = abs(light_angle - angle)
            if distance < min_distance:
                min_distance = distance
                nearest_led_id = i

        return nearest_led_id

    def set_led_angle(self, angle):
        # print(f"设置角度: {angle}°")
        # led_index = self.angle_to_led_index(angle)
        led_index = self.find_nearest_led(angle)
        led_index = (led_index+self.led_index_offset)%len(self.lights)
        # print(led_index)
        self.serial_manager.send_data(f'{led_index}+')

    def angle_to_led_index(self, angle):
        total_leds = self.leds_per_strip * self.num_strips
        # 每个LED对应的角度
        angle_per_led = 360 / total_leds
        led_per_angle = total_leds/360
        return int(angle*(led_per_angle))
