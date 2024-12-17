import serial
import time

class ServoController:
    def __init__(self, port, baudrate=115200):
        # 初始化串口通信
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)

    def send_command(self, command):
        """
        发送指令到舵机
        :param command: 指令字符串
        """
        full_command = f"#{command}!"  # 在指令前后加上 "#" 和 "!"
        self.ser.write(full_command.encode('utf-8'))
        time.sleep(0.1)  # 等待舵机响应

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
        command = f"{servo_id_str}P{pwm_str}{time_str}"
        self.send_command(command)
    
    def get_version(self, servo_id):
        """
        读取舵机版本
        :param servo_id: 舵机的 ID（3 位）
        :return: 舵机版本
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PVER"
        self.send_command(command)
        # 假设舵机会返回版本号，可以根据实际返回的数据格式来解析
        response = self.ser.readline().decode('utf-8').strip()
        return response

    def get_position(self, servo_id):
        """
        读取舵机当前位置
        :param servo_id: 舵机的 ID（3 位）
        :return: 舵机当前位置
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PRAD"
        self.send_command(command)
        response = self.ser.readline().decode('utf-8').strip()
        return response
    
    def release_torque(self, servo_id):
        """
        释放舵机的扭矩
        :param servo_id: 舵机的 ID（3 位）
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PULK"
        self.send_command(command)

    def restore_torque(self, servo_id):
        """
        恢复舵机的扭矩
        :param servo_id: 舵机的 ID（3 位）
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PULR"
        self.send_command(command)
    
    def stop_servo(self, servo_id):
        """
        停止舵机运动，保持当前位置
        :param servo_id: 舵机的 ID（3 位）
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PDST"
        self.send_command(command)

    def pause_servo(self, servo_id):
        """
        暂停舵机
        :param servo_id: 舵机的 ID（3 位）
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PDPT"
        self.send_command(command)
    
    def resume_servo(self, servo_id):
        """
        继续舵机运动
        :param servo_id: 舵机的 ID（3 位）
        """
        servo_id_str = f"{servo_id:03d}"
        command = f"{servo_id_str}PDCT"
        self.send_command(command)

if __name__ == "__main__":
    # 创建一个 ServoController 实例
    controller = ServoController(port='/dev/ttyUSB0', baudrate=9600)

    # 设置舵机 001 的 PWM 为 1500，运动时间为 1000 毫秒
    controller.set_pwm(1, 1500, 1000)

    # 获取舵机 001 的版本
    version = controller.get_version(1)
    print(f"舵机版本: {version}")

    # 获取舵机 001 的位置
    position = controller.get_position(1)
    print(f"舵机位置: {position}")

    # 释放舵机扭矩
    controller.release_torque(1)

    # 恢复舵机扭矩
    controller.restore_torque(1)
    
    # 停止舵机
    controller.stop_servo(1)

    # 暂停舵机
    controller.pause_servo(1)

    # 恢复舵机
    controller.resume_servo(1)
