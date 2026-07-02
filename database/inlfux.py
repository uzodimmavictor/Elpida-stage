class InfluxDB(DatabaseInterface):
    def __init__(self, host, port, database, user, password):
        super().__init__(host, port, user, password, database)
        self.connection = None
        