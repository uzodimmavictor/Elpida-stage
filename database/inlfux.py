from base_interface import DatabaseInterface
from influxdb import InfluxDBClient


class InfluxDB(DatabaseInterface):
    def __init__(self, url, port, username, password , database):
        super().__init__(url, port, username, password , database)
        self.connection = None

    def connect(self):
        self.connection = InfluxDBClient(
            host=self.url,
            port=self.port, 
            username=self.username, 
            password=self.password
        )
        self.connection.switch_database("dbinflux")
    def disconnect(self):
        if self.connection is not None:
            print("Closing PostgreSQL connection...")
            self.connection.close() # Native influxdb close method
            self.connection = None