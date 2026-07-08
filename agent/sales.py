from component.component import Component
from component.component_registry import registry
from component.dependency import Dependency
from database.postgres import PostgresDB

import threading
import time

@registry("AgentSales")
class AgentSales(Component):
    dependencies = [
        Dependency[PostgresDB]("dbPostgres", PostgresDB)
    ]

    def __init__(self, nom, isConfigurable):
        super().__init__(nom, isConfigurable)
        self.api_key = None
        self.running = False
        self.thread = None

    def configure(self, config_data):
        self.api_key = config_data.get("api_key")

    def isConfigured(self) -> bool:
        return self.api_key is not None

    def onEnterLoop(self) -> bool:
        self.running = True
        self.thread = threading.Thread(target=self.run_agent, daemon=True)
        self.thread.start()
        return True

    def run_agent(self):
        while self.running:
            print(f"[{self.nom}] Thread running... doing sales tasks with DB {self.getDependency('dbPostgres', PostgresDB).nom}")
            time.sleep(30)

    def onEnterLoopBefore(self):
        db: PostgresDB = self.getDependency("dbPostgres", PostgresDB)
        print(f"[{self.nom}] AgentSales is ready! I am successfully linked to database: {db.nom} at {db.url}:{db.port}")

    def disconnect(self):
        print(f"[{self.nom}] Shutting down AgentSales...")
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2)
