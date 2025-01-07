import time


class ServoController:
    def __init__(self, serial_manager):
        """
        初始化舵机控制类
        :param serial_manager: 串口管理实例
        """
        self.serial_manager = serial_manager
        self.last_pwm = -1

    def send_command(self, command):
        """
        发送舵机控制指令
        :param command: 指令字符串
        """
        full_command = f"#{command}!"
        self.serial_manager.send_data(full_command)
        time.sleep(0.1)

    def check_pwm(self, pwm):
        min = 1000
        max = 2000
        if self.last_pwm != -1:
            servo_id_str = f"{0:03d}"
            pwm_str = f"{pwm:04d}"
            time_str = f"{1:04d}"
            if pwm < min and self.last_pwm > max:
                self.set_mode(0, 7)
                command = f"{servo_id_str}P{pwm_str}T{time_str}"
                self.send_command(command)
                time.sleep(0.01)
                self.stop_servo(0)
                time.sleep(0.01)
                self.half_reset(0)
                time.sleep(0.01)
                self.stop_servo(0)
                time.sleep(0.1)
                print("sdfsd")
                # pass
            # elif pwm > max and self.last_pwm < min:
            #     self.set_mode(0, 8)
            #     self.set_angle(0, 360)
            #     self.stop_servo(0)
            #     self.half_reset(0)
            #     self.stop_servo(0)
            #     time.sleep(0.1)

    def set_pwm(self, servo_id, pwm, time_ms):
        """
        设置舵机的 PWM 和运行时间
        :param servo_id: 舵机的 ID（3 位）
        :param pwm: PWM 值（4 位）
        :param time_ms: 运行时间（4 位，单位：毫秒）
        """
        servo_id_str = f"{servo_id:03d}"
        pwm_str = f"{pwm:04d}"
        time_str = f"{time_ms:04d}"
        # self.check_pwm(pwm)
        self.last_pwm = pwm
        command = f"{servo_id_str}P{pwm_str}T{time_str}"
        self.send_command(command)

    def set_angle(self, servo_id, angle, time_ms=0):
        """
        设置舵机的角度
        :param servo_id: 舵机的 ID（3 位）
        :param angle: 角度（0-360°）
        :param time_ms: 运行时间（可选，单位：毫秒，默认 0）
        """
        max_angle = 360
        if not (0 <= angle <= max_angle):
            raise ValueError("角度必须在 0 到 180 之间")

        # 根据角度计算 PWM 值
        pwm = int(500 + (angle * (2500 - 500) / max_angle))

        # print(f'pwm:{pwm};angle:{angle};')

        # 调用 set_pwm 设置 PWM 和时间
        self.set_pwm(servo_id, pwm, time_ms)

    def get_version(self, servo_id):
        """
        读取舵机版本
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PVER"
        self.send_command(command)
        response = self.serial_manager.receive_data()
        print(f"舵机版本: {response}")
        return response

    def stop_servo(self, servo_id):
        """
        停止舵机运动
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PDST"
        self.send_command(command)

    def release_torque(self, servo_id):
        """
        释放舵机扭矩
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PULK"
        self.send_command(command)

    def restore_torque(self, servo_id):
        """
        恢复舵机扭矩
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PULR"
        self.send_command(command)

    def set_mode(self, servo_id, mode):
        """
        设置舵机的工作模式
        :param servo_id: 舵机的 ID
        :param mode: 模式编号（1-8）
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PMOD{mode}"
        self.send_command(command)

    def get_angle_from_pwm(self, pwm_value):
        """
        根据 PWM 值计算当前角度
        :param pwm_value: 当前 PWM 值
        :return: 计算得到的角度（0°到180°）
        """
        # 假设舵机的 PWM 范围是 500 - 2500，对应的角度范围是 0° - 180°
        min_pwm = 500
        max_pwm = 2500
        min_angle = 0
        max_angle = 360

        # 计算角度
        angle = (pwm_value - min_pwm) / (max_pwm -
                                         min_pwm) * (max_angle - min_angle)
        return angle

    def get_position(self, servo_id):
        """
        获取舵机的当前位置
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PRAD"
        self.send_command(command)
        response = self.serial_manager.receive_data()
        return response

    def get_current_angle(self, servo_id):
        """
        获取舵机当前的角度
        :param servo_id: 舵机的 ID
        :return: 当前角度值
        """
        # 获取舵机当前位置的 PWM 值
        response = self.get_position(servo_id)

        # 假设返回的 response 是 "P1500!" 形式的字符串
        if response.startswith("P"):
            pwm_value = int(response[1:5])  # 获取 PWM 值，假设为四位数
            angle = self.get_angle_from_pwm(pwm_value)  # 根据 PWM 计算角度
            return angle
        else:
            return None

    def set_baudrate(self, servo_id, baudrate):
        """
        设置舵机的通信波特率
        :param servo_id: 舵机的 ID
        :param baudrate: 波特率编号（1-8）
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PBD{baudrate}"
        self.send_command(command)

    def set_correction(self, servo_id):
        """
        纠正舵机偏差，将当前位置设置为1500
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PSCK"
        self.send_command(command)

    def set_startup_position(self, servo_id):
        """
        设置舵机启动位置
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PCSD"
        self.send_command(command)

    def remove_initial_value(self, servo_id):
        """
        去除舵机的初始值
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PCSM"
        self.send_command(command)

    def restore_initial_value(self, servo_id):
        """
        恢复舵机的初始值
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PCSR"
        self.send_command(command)

    def set_min_value(self, servo_id):
        """
        设置舵机的最小值
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PSMI"
        self.send_command(command)

    def set_max_value(self, servo_id):
        """
        设置舵机的最大值
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PSMX"
        self.send_command(command)

    def half_reset(self, servo_id):
        """
        半恢复出厂设置
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PCLE0"
        self.send_command(command)

    def full_reset(self, servo_id):
        """
        全恢复出厂设置
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PCLE"
        self.send_command(command)

    def get_temp_voltage(self, servo_id):
        """
        获取舵机的温度和电压
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PRTE"
        self.send_command(command)
        response = self.serial_manager.receive_data()
        return response

    def pause_servo(self, servo_id):
        """
        暂停舵机的当前操作
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PDPT"
        self.send_command(command)

    def continue_servo(self, servo_id):
        """
        恢复舵机的暂停操作
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PDCT"
        self.send_command(command)
