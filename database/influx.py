import re

from database.base_interface import DatabaseInterface
from component.component import Component
from component.component_registry import registry
from influxdb import InfluxDBClient

@registry("Influx")
class InfluxDB(Component, DatabaseInterface):
    def __init__(self, nom, isConfigurable):
        super().__init__(nom, isConfigurable)
        self.connection = None
        self.url = None
        self.port = None
        self.username = None
        self.password = None
        self.database = None

    def configure(self, config_data):
        self.url = config_data.get("url", "localhost")
        self.port = config_data.get("port", 8086)
        self.username = config_data.get("username", "")
        self.password = config_data.get("password", "")
        self.database = config_data.get("database", "dbinflux")

    def isConfigured(self):
        return self.url is not None and self.port is not None and self.database is not None

    def onEnterLoopAfter(self) -> bool:
        try:
            self._connect()
            return True
        except RuntimeError as exc:
            print(f"[{self.nom}] Failed to connect: {exc}")
            return False

    def _connect(self):
        try:
            from influxdb import InfluxDBClient
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency 'influxdb'. Install project dependencies with "
                "'pip install -r requirements.txt'."
            ) from exc
            

        self.connection = InfluxDBClient(
            host=self.url,
            port=self.port,
            username=self.username,
            password=self.password,
        )
        self.connection.switch_database(self.database)
        print(f"[{self.nom}] Connected to InfluxDB database '{self.database}'.")

    def disconnect(self):
        if self.connection is not None:
            print(f"Closing {self.nom} (InfluxDB) connection...")
            self.connection.close()
            self.connection = None

    def execute_request(self, query):
        if self.connection is None:
            raise RuntimeError(f"[{self.nom}] Cannot execute query: not connected.")
        return self.connection.query(query)
