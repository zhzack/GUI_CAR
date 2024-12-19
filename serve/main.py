from SerialManager import SerialManager
from ServoController import ServoController
from ws2812 import Ws2812
import time


def set_angle(angle):
    ws2812.set_led_angle(angle)
    time.sleep(0.01)
    servo.set_angle(servo_id, angle, time_ms)
    time.sleep(0.01)  # 延迟 1 秒


if __name__ == "__main__":
    # 创建串口管理实例
    serial_manager = SerialManager(default_baudrate=115200)
    ws2812 = Ws2812(serial_manager)

    # 扫描可用端口
    ports = serial_manager.scan_ports()
    print("可用端口列表:", ports)

    # 匹配端口
    port_name = serial_manager.match_port_by_keyword("21")
    if port_name:
        serial_manager.set_port(port_name)
    else:
        raise SystemExit("未找到匹配的串口")

    # 连接到串口
    serial_manager.connect()

    # 创建舵机控制实例
    servo = ServoController(serial_manager)
    servo_id = 0
    time_ms = 5
    angle = 310
    # pos = servo.get_position(servo_id)
    # print(pos)
    # servo.set_angle(servo_id, angle, time_ms)
    # time.sleep(0.5)
    # pos = servo.get_position(servo_id)
    # print(pos)

    try:
        while True:
            set_angle(angle)
            angle = (angle+1) % 360

        # # 示例操作：设置 PWM 和时间
        # servo.set_pwm(servo_id, pwm=2500, time_ms=1000)

        # # 读取舵机版本
        # version = servo.get_version(servo_id)
        # print(f"舵机版本: {version}")

        # # 停止舵机
        # servo.stop_servo(servo_id)

    except KeyboardInterrupt:
        print("程序中断")

    finally:
        # 断开串口连接
        serial_manager.disconnect()
