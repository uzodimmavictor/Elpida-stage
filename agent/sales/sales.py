from agent.sales import sales_aggregator
from component.component import Component
from component.component_registry import registry
from component.dependency import Dependency
from database.postgres import PostgresDB
from messaging.kafka import KafkaProducer
from aggregator import Aggregator
from train import Trainer


import threading
import time
from datetime import datetime, timezone

from ml.pipeline import pipeline

## add pipeline here attribute

@registry("AgentSales")
class AgentSales(Component):
    dependencies = [
        Dependency[PostgresDB]("dbPostgres", PostgresDB),
        Dependency[KafkaProducer]("kafkaProducer", KafkaProducer),
    ]

    aggregator: Aggregator
    train: Trainer

    def pipeline(self):
        data = self.aggregator.getData()
        self.train.train(data)
        pass
        
    def __init__(self, nom, isConfigurable):
        super().__init__(nom, isConfigurable)
        self.api_key = None
        self.suggestions_topic = None
        self.running = False
        self.thread = None

    def configure(self, config_data):
        self.api_key = config_data.get("api_key")
        self.suggestions_topic = config_data.get(
            "suggestions_topic", "sales-suggestions",
        )
        self.period = config_data.get("period", 300)
        

    def isConfigured(self) -> bool:
        return self.api_key is not None and self.suggestions_topic is not None

    def onEnterLoop(self) -> bool:
        ## call pipeline into thread each period
        
        self.running = True
        self.thread = threading.Thread(target=self.run_agent, daemon=True)
        self.thread.start()
        return True

    def run_agent(self):
        while self.running:
            db = self.getDependency("dbPostgres", PostgresDB)
            kafka = self.getDependency("kafkaProducer", KafkaProducer)
            suggestion = self.build_sales_suggestion(db)

            kafka.publish(self.suggestions_topic, suggestion)
            print(
                f"[{self.nom}] Published sales suggestion using DB dependency "
                f"{db.nom}."
            )
            time.sleep(30)
        
        
    def onEnterLoopBefore(self):
        
        db: PostgresDB = self.getDependency("dbPostgres", PostgresDB)
        kafka: KafkaProducer = self.getDependency("kafkaProducer", KafkaProducer)
        print(
            f"[{self.nom}] AgentSales is ready. Linked to database "
            f"{db.nom} at {db.url}:{db.port} and Kafka component {kafka.nom}."
        )

    def build_sales_suggestion(self, db):
        return {
            "agent": self.nom,
            "type": "sales_suggestion",
            "source_database": db.nom,
            "suggestion": "review_recent_paniers",
            "reason": "AgentSales runtime loop is active.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def disconnect(self):
        print(f"[{self.nom}] Shutting down AgentSales...")
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2)
