from abc import ABC, abstractmethod
class Component(ABC):
     def __init__(self, nom, isConfigurable):
         self.nom = nom
         self.isConfigurable = isConfigurable
     @abstractmethod
     def configure(self, config_data):
         pass
        
     @abstractmethod
     def isConfigured(self) -> bool:
        pass