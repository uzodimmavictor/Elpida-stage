from base_interface import DatabaseInterface
import psycopg2

class PostgresDB(DatabaseInterface):
    def __init__(self, url, port, username, password , database):
        super().__init__(url, port, username, password , database)
        self.connection = None
        
    def connect(self):
        self.connection = psycopg2.connect(
            host=self.url,
            port=self.port,
            database=self.database,
            user=self.username,
            password=self.password
        )
        cursor = self.connection.cursor()
        print("Pinging PostgreSQL...")
        cursor.execute("SELECT version();")
    
        db_version = cursor.fetchone()
        print("Success! You are connected to:")
        print(f"   -> {db_version[0]}")
        
    def disconnect(self):
        if self.connection is not None:
            print("Closing PostgreSQL connection...")
            self.connection.close()
            self.connection = None