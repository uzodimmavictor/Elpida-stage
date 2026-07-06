from typing import Generic, TypeVar

T = TypeVar("T")


class Dependency(Generic[T]):
    def __init__(self, name: str, dep_type: type[T]):
        self.name = name
        self.dep_type = dep_type