from component.component import Component
from component.component_registry import registry
from component.dependency import Dependency
from database.postgres import PostgresDB
from messaging.kafka import KafkaProducer

import threading
import time
from datetime import datetime, timezone
from pathlib import Path
import joblib

from agent.sales.pipeline import SalesPipeline


@registry("AgentSales")
class AgentSales(Component):
    dependencies = [
        Dependency[PostgresDB]("dbPostgres", PostgresDB),
        Dependency[KafkaProducer]("kafkaProducer", KafkaProducer),
    ]

    def __init__(self, nom, isConfigurable):
        super().__init__(nom, isConfigurable)
        self.api_key = None
        self.suggestions_topic = None
        self.period = 300
        self.running = False
        self.thread = None
        self.model = None
        self.model_path = Path(__file__).parent / "sales_model.pkl"

    def configure(self, config_data):
        self.api_key = config_data.get("api_key")
        self.suggestions_topic = config_data.get(
            "suggestions_topic", "sales-suggestions",
        )
        self.period = config_data.get("period", 300)

    def isConfigured(self) -> bool:
        return self.api_key is not None and self.suggestions_topic is not None

    def onEnterLoopBefore(self):
        db: PostgresDB = self.getDependency("dbPostgres", PostgresDB)
        kafka: KafkaProducer = self.getDependency("kafkaProducer", KafkaProducer)
        print(
            f"[{self.nom}] Linked to database {db.nom} and Kafka {kafka.nom}."
        )
        self.pipeline = SalesPipeline(db.connection, self.model_path)
        self._pipeline()
        self._load_model()

    def onEnterLoopAfter(self) -> bool:
        return True

    def onEnterLoop(self) -> bool:
        self.running = True
        self.thread = threading.Thread(target=self.run_agent, daemon=True)
        self.thread.start()
        return True

    def _pipeline(self):
        try:
            self.pipeline.run()
        except Exception as e:
            print(f"[{self.nom}] Pipeline training failed: {e}")

    def _load_model(self):
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            print(f"[{self.nom}] Loaded model from {self.model_path}")
        else:
            print(f"[{self.nom}] No model found at {self.model_path}")

    def run_agent(self):
        while self.running:
            db = self.getDependency("dbPostgres", PostgresDB)
            kafka = self.getDependency("kafkaProducer", KafkaProducer)

            if not kafka.isConnected():
                print(f"[{self.nom}] Kafka not connected, reconnecting...")
                kafka.connect()

            suggestion = self.build_sales_suggestion(db)
            if kafka.publish(self.suggestions_topic, suggestion):
                print(f"[{self.nom}] Published to '{self.suggestions_topic}'.")
            else:
                print(f"[{self.nom}] Failed to publish to '{self.suggestions_topic}'.")

            time.sleep(self.period)

    def build_sales_suggestion(self, db):
        if self.model is None:
            return self._fallback_suggestion(db)

        try:
            features = self.pipeline.aggregator.fetch_recent_features()

            if features.empty:
                return {
                    "agent": self.nom,
                    "type": "sales_suggestion",
                    "source_database": db.nom,
                    "suggestion": "no_recent_data",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }

            predictions = self.model.predict(features)
            probabilities = self.model.predict_proba(features)[:, 1]
            avg_confidence = sum(probabilities) / len(probabilities)
            suggestion = "follow_up_high_value" if avg_confidence > 0.5 else "monitor_active"

            return {
                "agent": self.nom,
                "type": "sales_suggestion",
                "source_database": db.nom,
                "suggestion": suggestion,
                "reason": f"ML predicts avg confidence {avg_confidence:.2f} from {len(predictions)} paniers.",
                "paniers_analyzed": len(predictions),
                "avg_confidence": round(avg_confidence, 3),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            print(f"[{self.nom}] Prediction error: {e}")
            return self._fallback_suggestion(db)

    def _fallback_suggestion(self, db):
        return {
            "agent": self.nom,
            "type": "sales_suggestion",
            "source_database": db.nom,
            "suggestion": "review_recent_paniers",
            "reason": "AgentSales runtime loop is active.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def disconnect(self):
        print(f"[{self.nom}] Shutting down...")
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2)
