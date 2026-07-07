from abc import ABC, abstractmethod
from typing import TypeVar
from .dependency import Dependency

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
        
      ## should be modified  
     def setDependency(self, name: str, component: object) -> None:
         ## check type procces component == dependency        
        self._dependencies[name] = component

     def getDependency(self, name: str, typ: type[T]) -> T:
        value = self._dependencies.get(name)
        if value is None:
            raise KeyError(f"Dependency '{name}' not found")
        if not isinstance(value, typ):
            raise TypeError(f"Dependency '{name}' is not of type {typ.__name__}")
        return value

     def isReady(self) -> bool:
        if hasattr(self, 'dependencies'):
            for dep in self.dependencies:
                if dep.name not in self._dependencies:
                    return False
                if not isinstance(self._dependencies[dep.name], dep.dep_type):
                    return False
        return True

     def onEnterLoopBefore(self) -> bool:
         return True
         pass

     def onEnterLoopAfter(self) -> bool:
        return True
        pass

     def onEnterLoop(self) -> bool:
        return True
        pass