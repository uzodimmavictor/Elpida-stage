from abc import ABC, abstractmethod


class Aggregator(ABC):
    @abstractmethod
    def getData(self):
        pass
