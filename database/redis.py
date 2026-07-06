import shlex

from component.component import Component
from component.component_registry import registry
from database.base_interface import DatabaseInterface


@registry("Redis")
class RedisDB(Component, DatabaseInterface):
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
        self.port = config_data.get("port", 6379)
        self.username = config_data.get("username") or None
        self.password = config_data.get("password") or None
        self.database = config_data.get("database", 0)

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
            import redis
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency 'redis'. Install project dependencies with "
                "'pip install -r requirements.txt'."
            ) from exc

        self.connection = redis.Redis(
            host=self.url,
            port=self.port,
            username=self.username,
            password=self.password,
            db=self.database,
            decode_responses=True,
        )
        self.connection.ping()
        print(f"[{self.nom}] Connected to Redis database {self.database}.")

    def disconnect(self):
        if self.connection is not None:
            print(f"Closing {self.nom} (Redis) connection...")
            self.connection.close()
            self.connection = None

    def execute_request(self, query):
        if self.connection is None:
            raise RuntimeError(f"[{self.nom}] Cannot execute query: not connected.")

        command = shlex.split(query) if isinstance(query, str) else query
        if not isinstance(command, (list, tuple)) or len(command) == 0:
            raise ValueError("Redis query must be a command string or a non-empty list/tuple.")
        return self.connection.execute_command(*command)
