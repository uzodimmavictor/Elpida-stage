from component.component import Component
from component.component_registry import registry
from database.base_interface import DatabaseInterface


@registry("Postgres")
class PostgresDB(Component, DatabaseInterface):
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
        self.port = config_data.get("port", 5432)
        self.username = config_data.get("username", "postgres")
        self.password = config_data.get("password", "postgres")
        self.database = config_data.get("database", "postgres")

    def isConfigured(self):
        return all([self.url, self.port, self.username, self.password, self.database])

    def connect(self):
        try:
            import psycopg2
        except ImportError:
            print(
                f"[{self.nom}] Missing dependency 'psycopg2'. "
                "Install it with 'pip install -r requirements.txt'."
            )
            return False

        try:
            self.connection = psycopg2.connect(
                host=self.url,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
            )
            print(f"[{self.nom}] Connected to PostgreSQL database '{self.database}'.")
            return True
        except Exception as exc:
            self.connection = None
            print(f"[{self.nom}] Failed to connect: {exc}")
            return False

    def onEnterLoopAfter(self) -> bool:
        if self.connection is None:
            return self.connect()
        return True

    def disconnect(self):
        if self.connection is not None:
            print(f"Closing {self.nom} (PostgreSQL) connection...")
            self.connection.close()
            self.connection = None

    def execute_request(self, query):
        if self.connection is None:
            raise RuntimeError(f"[{self.nom}] Cannot execute query: not connected.")

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            if cursor.description is None:
                self.connection.commit()
                return None
            return cursor.fetchall()
