import base64
from datetime import datetime
import random
import time
import json
import os
from paho.mqtt import client as mqtt_client


class MQTTClient:
    def __init__(self):
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(
            self.current_path, "config", "config.json")
        self.default_config_path = os.path.join(
            self.current_path, "config", "default_config.json"
        )
        self.config = self.load_config()
        self.res_topics = self.config.get("res_topics", {})
        self.robot_topics = self.config.get("robot_topics", [])

        self.broker = self.config.get("broker")
        self.port = self.config.get("port")
        self.keepalive_interval = self.config.get("keepalive_interval")
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.pub_config = self.config.get("pub_config")
        self.client_id = f"python-mqtt-{random.randint(0, 1000)}"
        self.client = mqtt_client.Client(
            mqtt_client.CallbackAPIVersion.VERSION1, self.client_id
        )
        self.on_connect_callback = None
        self.on_message_callback = None

    # @property
    # def value(self):
    #     return self._value

    # @value.setter
    # def value(self, value):
    #     if self._value != value:
    #         print(f"Value changed from {self._value} to {value}")
    #     self._value = value

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as file:
                    return json.load(file)
            else:
                return self.load_default_config()
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"读取配置文件出错，使用默认设置: {e}")
            return self.load_default_config()

    def load_default_config(self):
        with open(self.default_config_path, "r") as file:
            default_config = json.load(file)
            with open(self.config_path, "w") as file:
                json.dump(default_config, file, indent=4)
            return default_config
        
    def save_config(self, new_config):
        """保存当前配置到文件中"""
        try:
            with open(self.config_path, "w") as file:
                json.dump(new_config, file, indent=4)
            print("配置已保存成功")
        except Exception as e:
            print(f"保存配置文件出错: {e}")

    def connect(self):
        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker, self.port,
                            keepalive=self.keepalive_interval)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        status = "连接到MQTT Broker!" if rc == 0 else f"连接失败，返回码 {rc}"
        if self.on_connect_callback:
            self.on_connect_callback(status)

    def subscribe(self, topics):
        for topic in topics:
            self.client.subscribe(topic)
        self.client.on_message = self.on_message

    def on_message(self, client, userdata, msg):
        self.on_message_received(msg)
        if self.on_message_callback:
            self.on_message_callback(msg)

    def set_on_connect_callback(self, callback):
        self.on_connect_callback = callback

    def set_on_message_callback(self, callback):
        self.on_message_callback = callback

    def publish(self, topic, message):
        result = self.client.publish(topic, message)
        status = result[0]
        if status == 0:
            print(f"发送消息到主题 `{topic}`成功")
        else:
            print(f"发送消息到主题 `{topic}` 失败")
        return status

    def read_file_as_base64(self, file_path):
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    def pub_send_task_file(self, file_path):

        send_task_file = self.pub_config["send_task_file"]
        topic = send_task_file["topic"]
        data = send_task_file["send_task_file"]
        data["file_name"] = os.path.basename(file_path)
        data["basecode"] = self.read_file_as_base64(file_path)
        self.publish(topic, json.dumps(data))

    def pub_task_set(self):
        task_set = self.config["pub_config"]["task_set"]
        topic = task_set["topic"]
        data = task_set["task_set"]
        print("设置任务成功")

        self.save_config(self.config)

        self.publish(topic, json.dumps(data))

    def pub_task_control(self, cmd=0, start_from_id=0):
        # cmd
        # 0: 暂停任务
        # 1：开始任务
        # 2：任务终⽌
        # start_from_id
        # 任务节点按照1...N进⾏编号， start_from_id 标识从第⼏个任务点开始进⾏任务，之前编号的任
        # 务点将被跳过。
        control = self.config["pub_config"]["control"]
        topic = control["topic"]
        data = control["control"]
        data['cmd'] = cmd
        if start_from_id:
            data['start_from_id'] = start_from_id
        self.publish(topic, json.dumps(data))

    def pub_setting(self, heatbeat_interval=None, max_vehicle_speed_limit=None, min_vehicle_speed_limit=None, robot_arm_speed_rate=None):

        setting = self.config["pub_config"]["setting"]
        topic = setting["topic"]
        data = setting["setting"]
        if heatbeat_interval:
            # int值，表示多少毫秒ms上传依次
            data['heatbeat_interval'] = heatbeat_interval
        if max_vehicle_speed_limit:
            #   3.0, // double, 最⾼速度限制，km/h
            data['max_vehicle_speed_limit'] = max_vehicle_speed_limit
        if min_vehicle_speed_limit:
            #  1.0, // double, 最低速度限制, km/h
            data['min_vehicle_speed_limit'] = min_vehicle_speed_limit
        if robot_arm_speed_rate:
            #   0.25 // double，机械臂速度, m/s
            data['robot_arm_speed_rate'] = robot_arm_speed_rate

        self.publish(topic, json.dumps(data))

    def is_connected(self):
        return self.client.is_connected()

    def run(self, user_data, robot_topics, res_topics):
        self.connect()
        self.subscribe(robot_topics + list(res_topics.values()))
        # while True:
        #     time.sleep(5)
        #     task_set_ = user_data["task_set"]
        #     task_set_["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #     self.pub_send_task_file(
        #         f"{os.path.dirname(os.path.realpath(__file__))}/CreatJsonforCirclePath/CirclePath_Rad2m.json", user_data
        #     )

    def on_message_received(self, msg):
        # print(msg.topic)
        if msg.topic in self.robot_topics:
            if msg.topic == self.robot_topics[0]:
                self.handle_robot_heart_beat(msg)
            else:
                self.handle_robot_message(msg)
        elif msg.topic in self.res_topics.values():
            self.handle_res_message(msg)

    def merge_data(self, msg):
        payload = json.loads(msg.payload)
        pose = payload.get("pose", {})
        task_status = payload.get("task_status", "未知")
        current_task_id = payload.get("current_task_id", "未知")
        time_stamp = payload.get("timestamp", "未知")
        current_robot_status = payload.get("current_robot_status", "未知")

        msg_object = {
            "local_angle": pose.get("local_angle", 0),
            "local_x": pose.get("local_x", 0),
            "local_y": pose.get("local_y", 0),
            "current_task_id": current_task_id,
            "latitude": pose.get("latitude", 0),
            "longitude": pose.get("longitude", 0),
            "altitude": pose.get("altitude", 0),
            "rev_time": int(time.time() * 1000),
            "timestamp": time_stamp,
            "task_status": task_status,
            "current_robot_status": current_robot_status,
            "topic": msg.topic,
        }

        # print(msg_object)
        return msg_object

    def handle_robot_heart_beat(self, msg):
        msg_object = self.merge_data(msg)
        # self.plot_mqtt.update_plot(msg_object["local_x"], msg_object["local_y"])
        # self.mqtt_res_obj = self.merge_data(msg)

        # self.message_display.append(str(msg_object))
        # self.message_display.verticalScrollBar().setValue(
        #     self.message_display.verticalScrollBar().maximum()
        # )

    def handle_robot_message(self, msg):
        # self.robot_message_label.setText(
        #     f"Robot Topic `{msg.topic}`: {msg.payload.decode()}"
        # )
        print(f"Robot Topic `{msg.topic}`: {msg.payload.decode()}")

    def handle_task_set_response(self, payload, code):
        print(f"Task Set Response: {payload}, code: {code}")

    def handle_control_response(self, payload, code):
        print(f"Control Response: {payload}, code: {code}")

    def handle_setting_response(self, payload, code):
        print(f"Setting Response: {payload}, code: {code}")

    def handle_send_task_file_response(self, payload, code):
        print(f"Send Task File Response: {payload}, code: {code}")
        # self.show_message(f"发布结果: {code}", f"{payload}")

    def handle_request_task_file_response(self, payload, code):
        print(f"Request Task File Response: {payload}, code: {code}")

    def handle_res_message(self, msg):
        try:
            payload = json.loads(msg.payload.decode())
            code = payload.get("code", None)
            print(code)
            topic_handlers = {
                self.res_topics.get("task_set"):
                    self.handle_task_set_response,

                self.res_topics.get("control"):
                    self.handle_control_response,

                self.res_topics.get("setting"):
                    self.handle_setting_response,

                self.res_topics.get("send_task_file"):
                    self.handle_send_task_file_response,

                self.res_topics.get("request_task_file"):
                    self.handle_request_task_file_response,
            }
            handler = topic_handlers.get(msg.topic)
            if handler:
                handler(payload, code)
            else:
                print(f"Unhandled topic `{msg.topic}` with payload: {payload}")
        except json.JSONDecodeError:
            print(f"Received invalid JSON from `{
                  msg.topic}`: {msg.payload.decode()}")

# 使用示例（假设其他必要的代码如用户数据和主题已定义）：

# if __name__ == "__main__":
#     current_path = os.path.dirname(os.path.realpath(__file__))
#     config_path = os.path.join(current_path, "config", "config.json")
#     default_config_path = os.path.join(current_path, "config", "default_config.json")

#     mqtt_client = MQTTClient(config_path, default_config_path)

#     def on_connect_status(status):
#         print(status)

#     def on_message_received(msg):
#         print(f"收到消息: {msg.topic} {msg.payload.decode()}")

#     mqtt_client.set_on_connect_callback(on_connect_status)
#     mqtt_client.set_on_message_callback(on_message_received)

#     user_data = {
#         "task_set": {"task": "example_task"},
#         "control": {},
#         "arm_set": {},
#         "send_task_file": {},
#         "setting": {},
#         "request_task_file": {},
#     }

#     robot_topics = ["/sy/robot/heart_beat", "/sy/robot/message"]
#     res_topics = {
#         "task_set": "/sy/res/user/task_set",
#         "control": "/sy/res/user/control",
#         "setting": "/sy/res/user/setting",
#         "send_task_file": "/sy/res/user/send_task_file",
#         "request_task_file": "/sy/res/user/request_task_file",
#     }

#     mqtt_client.run(user_data, robot_topics, res_topics)
