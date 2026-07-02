from abc import ABC, abstractmethod

class SqlInterface(ABC):
    def __init__(self, url, port, username, password):
        self.url = url
        self.port = port
        self.username = username
        self.password = password

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def execute_request(self, query):
        pass