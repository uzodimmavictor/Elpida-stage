from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")

class Component(ABC):
     def __init__(self, nom, isConfigurable):
         self.nom = nom
         self.isConfigurable = isConfigurable
         self._dependencies: dict[str, object] = {}

     @abstractmethod
     def configure(self, config_data):
         pass
        
     @abstractmethod
     def isConfigured(self) -> bool:
        pass

     def setDependency(self, name: str, component: object) -> None:
        self._dependencies[name] = component

     def getDependency(self, name: str, typ: type[T]) -> T:
        value = self._dependencies.get(name)
        if value is None:
            raise KeyError(f"Dependency '{name}' not found")
        if not isinstance(value, typ):
            raise TypeError(f"Dependency '{name}' is not of type {typ.__name__}")
        return value