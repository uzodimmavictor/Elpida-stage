from component.component import Component
from component.component_registry import registry

import threading


@registry("KafkaConsumer")
class KafkaConsumer(Component):
    def __init__(self, nom, isConfigurable):
        super().__init__(nom, isConfigurable)
        self.bootstrap_servers = None
        self.group_id = None
        self.topics = None
        self.consumer = None
        self.running = False
        self.thread = None
        self.handlers = {}

    def configure(self, config_data):
        self.bootstrap_servers = config_data.get("bootstrap_servers", "localhost:9092")
        self.group_id = config_data.get("group_id", self.nom)
        self.topics = config_data.get("topics", [])

    def isConfigured(self) -> bool:
        return self.bootstrap_servers is not None

    def isConnected(self) -> bool:
        return self.consumer is not None

    def connect(self):
        try:
            from kafka import KafkaConsumer as KafkaPythonConsumer
        except ImportError:
            print(
                f"[{self.nom}] Missing dependency 'kafka-python'. "
                "Install it with 'pip install -r requirements.txt'."
            )
            return False

        try:
            self.consumer = KafkaPythonConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                enable_auto_commit=True,
            )
            print(
                f"[{self.nom}] Connected to Kafka at {self.bootstrap_servers}, "
                f"topics: {self.topics}."
            )
            return True
        except Exception as exc:
            self.consumer = None
            print(f"[{self.nom}] Failed to connect: {exc}")
            return False

    def subscribe(self, topic, handler):
        if topic not in self.topics:
            self.topics.append(topic)
        self.handlers[topic] = handler

    def onEnterLoopBefore(self) -> bool:
        if self.consumer is None:
            return self.connect()
        return True

    def onEnterLoop(self) -> bool:
        self.running = True
        self.thread = threading.Thread(target=self._poll, daemon=True)
        self.thread.start()
        return True

    def onEnterLoopAfter(self) -> bool:
        if self.isConnected():
            print(f"[{self.nom}] Consumer ready, polling {self.topics}.")
        return True

    def _poll(self):
        while self.running and self.consumer is not None:
            try:
                messages = self.consumer.poll(timeout_ms=1000)
                for topic_partition, records in messages.items():
                    topic = topic_partition.topic
                    handler = self.handlers.get(topic)
                    if handler is None:
                        continue
                    for record in records:
                        try:
                            handler(record.value)
                        except Exception as exc:
                            print(
                                f"[{self.nom}] Handler error for '{topic}': {exc}"
                            )
            except Exception as exc:
                if self.running:
                    print(f"[{self.nom}] Poll error: {exc}")

    def disconnect(self):
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=2)
        if self.consumer is not None:
            print(f"[{self.nom}] Closing consumer...")
            self.consumer.close()
            self.consumer = None
