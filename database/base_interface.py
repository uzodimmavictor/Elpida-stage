from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    def __init__(self, url, port, username, password , database):
        self.url = url
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def execute_request(self, query):
        pass