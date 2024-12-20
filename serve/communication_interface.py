from abc import ABC, abstractmethod

# 抽象基类 CommunicationInterface，定义了所有通信方式必须实现的方法


class CommunicationInterface(ABC):

    @abstractmethod
    def send_data(self, data: str):
        """
        抽象方法，所有子类必须实现。
        用于发送数据
        :param data: 要发送的数据，类型为字符串
        """
        pass

    @abstractmethod
    def receive_data(self):
        """
        抽象方法，所有子类必须实现。
        接收返回的数据
        :return: 返回的数据字符串
        """
        pass

    @abstractmethod
    def close(self):
        """
        抽象方法，所有子类必须实现。
        用于关闭连接（如果需要的话）。
        """
        pass
