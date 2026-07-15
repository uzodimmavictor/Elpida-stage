from collections import namedtuple

Pair = namedtuple("Pair", ["first", "second"])

class RestHandler:
    def __init__(self):
         pass


    @abstractmethod
    def process_request(self, request)-> Pair:
        pass 
    