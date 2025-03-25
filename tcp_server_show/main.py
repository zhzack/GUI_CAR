from serve.SerialManager import SerialManager
from serve.TCPServerManager import TCPServer
from serve.ServoController import ServoController


manager1 = SerialManager(port_by_keyword='CH', baudrate=115200)
        # self.manager = TCPServer(host='172.20.10.2', port=80)
manager = TCPServer(host='0.0.0.0', port=6666)