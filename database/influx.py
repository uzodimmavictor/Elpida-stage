from database.base_interface import DatabaseInterface
from component.component import Component
from component.component_registry import registry


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

    def connect(self):
        if not self.isConfigured():
            print(f"[{self.nom}] Cannot connect: not fully configured.")
            return

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
