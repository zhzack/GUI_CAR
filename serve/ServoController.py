import time

class ServoController:
    def __init__(self, serial_manager):
        """
        初始化舵机控制类
        :param serial_manager: 串口管理实例
        """
        self.serial_manager = serial_manager

    def send_command(self, command):
        """
        发送舵机控制指令
        :param command: 指令字符串
        """
        full_command = f"#{command}!"
        print(f"发送指令: {full_command}")
        self.serial_manager.send_data(full_command)
        time.sleep(0.1)

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
        command = f"{servo_id_str}P{pwm_str}T{time_str}"
        self.send_command(command)
    
    def set_angle(self, servo_id, angle, time_ms=0):
        """
        设置舵机的角度
        :param servo_id: 舵机的 ID（3 位）
        :param angle: 角度（0-180°）
        :param time_ms: 运行时间（可选，单位：毫秒，默认 0）
        """
        if not (0 <= angle <= 180):
            raise ValueError("角度必须在 0 到 180 之间")

        # 根据角度计算 PWM 值
        pwm = int(500 + (angle * (2500 - 500) / 180))
        
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

    def get_position(self, servo_id):
        """
        获取舵机的当前位置
        :param servo_id: 舵机的 ID
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PRAD"
        self.send_command(command)
        response = self.serial_manager.receive_data()
        print(f"舵机当前位置: {response}")
        return response

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
        print(f"舵机温度与电压: {response}")
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
