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
        if hasattr(self, "dependencies"):
            for dep in self.dependencies:
                if dep.name == name:
                    if not isinstance(component, dep.dep_type):
                        raise TypeError(
                            f"Cannot inject '{name}': Expected type {dep.dep_type.__name__}, "
                            f"got {type(component).__name__}"
                        )
                    break

        self._dependencies[name] = component

    def getDependency(self, name: str, typ: type[T]) -> T:
        value = self._dependencies.get(name)
        if value is None:
            raise KeyError(f"Dependency '{name}' not found")
        if not isinstance(value, typ):
            raise TypeError(f"Dependency '{name}' is not of type {typ.__name__}")
        return value

    def isReady(self) -> bool:
        if hasattr(self, "dependencies"):
            for dep in self.dependencies:
                if dep.name not in self._dependencies:
                    return False
                if not isinstance(self._dependencies[dep.name], dep.dep_type):
                    return False
        return True

    def onEnterLoopBefore(self) -> bool:
        return True

    def onEnterLoopAfter(self) -> bool:
        return True

    def onEnterLoop(self) -> bool:
        return True

    def eventReceived(self, event_name, event_data) -> bool:
        return False
