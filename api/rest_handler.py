from abc import ABC, abstractmethod
from collections import namedtuple

Pair = namedtuple("Pair", ["first", "second"])


class RestHandler(ABC):
    @abstractmethod
    def process_request(self, request) -> Pair:
        pass 
    