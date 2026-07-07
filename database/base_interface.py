from abc import ABC, abstractmethod


class DatabaseInterface(ABC):

    @abstractmethod
    def disconnect(self):
        """Each database must implement its own teardown logic here."""
        pass

    @abstractmethod
    def execute_request(self, query):
        pass
