import json

from component.component import Component
from component.component_registry import registry


@registry("KafkaProducer")
class KafkaProducer(Component):
    def __init__(self, nom, isConfigurable):
        super().__init__(nom, isConfigurable)
        self.bootstrap_servers = None
        self.client_id = None
        self.producer = None

    def configure(self, config_data):
        self.bootstrap_servers = config_data.get("bootstrap_servers", "localhost:9092")
        self.client_id = config_data.get("client_id", self.nom)

    def isConfigured(self) -> bool:
        return self.bootstrap_servers is not None

    def isConnected(self) -> bool:
        return self.producer is not None

    def connect(self):
        try:
            from kafka import KafkaProducer as KafkaPythonProducer
        except ImportError:
            print(
                f"[{self.nom}] Missing dependency 'kafka-python'. "
                "Install it with 'pip install -r requirements.txt'."
            )
            return False

        try:
            self.producer = KafkaPythonProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            )
            print(f"[{self.nom}] Connected to Kafka at {self.bootstrap_servers}.")
            return True
        except Exception as exc:
            self.producer = None
            print(f"[{self.nom}] Failed to connect to Kafka: {exc}")
            return False

    def publish(self, topic, message):
        if self.producer is None:
            print(f"[{self.nom}] Kafka not connected. Message not sent.")
            return False

        try:
            future = self.producer.send(topic, message)
            future.get(timeout=10)
            self.producer.flush()
            return True
        except Exception as exc:
            print(f"[{self.nom}] Failed to publish to '{topic}': {exc}")
            return False

    def onEnterLoopBefore(self) -> bool:
        if self.producer is None:
            return self.connect()
        return True

    def onEnterLoopAfter(self) -> bool:
        if self.isConnected():
            print(f"[{self.nom}] Kafka producer ready.")
        else:
            print(f"[{self.nom}] Kafka producer not available.")
        return True

    def disconnect(self):
        if self.producer is not None:
            print(f"[{self.nom}] Closing Kafka producer...")
            self.producer.close()
            self.producer = None
