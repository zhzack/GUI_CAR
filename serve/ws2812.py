class Ws2812:
    def __init__(self, serial_manager):
        self.serial_manager = serial_manager
        self.leds_per_strip = 144
        self.num_strips = 18
        self.led_num = self.leds_per_strip*self.num_strips

    def set_led_angle(self, angle):
        # print(f"设置角度: {angle}°")
        led_index = self.angle_to_led_index(angle)
        # print(led_index)
        self.serial_manager.send_data(f'{led_index}+')

    def angle_to_led_index(self, angle):
        total_leds = self.leds_per_strip * self.num_strips
        # 每个LED对应的角度
        angle_per_led = 360 / total_leds
        led_per_angle = total_leds/360
        return int(angle*(led_per_angle))

        # 计算LED的索引
        led_index = int(angle / angle_per_led)

        # 计算灯带和在灯带上的LED索引
        strip_index = led_index // leds_per_strip  # 灯带编号
        led_in_strip_index = led_index % leds_per_strip  # 该灯带中的LED索引
        return led_index
        # return strip_index, led_in_strip_index
