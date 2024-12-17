from SerialManager import SerialManager
from ServoController import ServoController
import time
if __name__ == "__main__":
    # 创建串口管理实例
    serial_manager = SerialManager(default_baudrate=115200)

    # 扫描可用端口
    ports = serial_manager.scan_ports()
    print("可用端口列表:", ports)

    # 匹配端口
    port_name = serial_manager.match_port_by_keyword("USB")
    if port_name:
        serial_manager.set_port(port_name)
    else:
        raise SystemExit("未找到匹配的串口")

    # 连接到串口
    serial_manager.connect()

    # 创建舵机控制实例
    servo = ServoController(serial_manager)
    servo_id = 0
    try:
        while True:
            # 从 0° 到 180° 旋转
            for angle in range(0, 181, 5):  # 以 10° 增加
                print(f"设置角度: {angle}°")
                servo.set_angle(servo_id=0, angle=angle, time_ms=500)
                time.sleep(0.5)  # 延迟 1 秒
            
            # 从 180° 到 0° 旋转
            for angle in range(180, -1, -5):  # 以 10° 减少
                print(f"设置角度: {angle}°")
                servo.set_angle(servo_id=0, angle=angle, time_ms=500)
                time.sleep(0.5)  # 延迟 1 秒
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
