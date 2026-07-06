from component.component import Component
from component.component_registry import registry
from component.dependency import Dependency
from database.postgres import PostgresDB

@registry("AgentSales")
class AgentSales(Component):
    dependencies = [
        Dependency[PostgresDB]("db", PostgresDB)
    ]

    def __init__(self, nom, isConfigurable):
        super().__init__(nom, isConfigurable)
        self.api_key = None

    def configure(self, config_data):
        self.api_key = config_data.get("api_key")

    def isConfigured(self) -> bool:
        return self.api_key is not None

    def connect(self):
        db: PostgresDB = self.getDependency("db", PostgresDB)
        print(f"[{self.nom}] AgentSales is ready! I am successfully linked to database: {db.nom} at {db.url}:{db.port}")

    def disconnect(self):
        print(f"[{self.nom}] Shutting down AgentSales...")
