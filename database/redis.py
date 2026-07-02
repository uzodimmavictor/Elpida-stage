from base_interface import DatabaseInterface
import redis

class RedisDB(DatabaseInterface):
    def __init__(self, url, port, username, password, database):
        super().__init__(url, port, username, password, database)
        self.connection = None

    def connect(self):  
        self.connection = redis.Redis(
                host=self.url, 
                port=self.port, 
                username=self.username, 
                password=self.password
            )
        self.connection.set('my_first_key', 'Connection ESTABLISHED')
        print(self.connection.get('my_first_key'))
        
    def disconnect(self):
        if self.connection is not None:
            print("Closing Redis connection...")
            self.connection.close()
            self.connection = None  