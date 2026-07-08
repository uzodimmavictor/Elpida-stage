import pandas as pd
import psycopg2

class DataAggregator:
    def __init__(self, db_config):
        self.db_config = db_config

    def connect(self):
        """Connects to the Postgres database."""
        return psycopg2.connect(
            host=self.db_config["url"],
            port=self.db_config["port"],
            database=self.db_config["database"],
            user=self.db_config["username"],
            password=self.db_config["password"]
        )

    def fetch_raw_data(self):
        """Fetches raw tables from Postgres."""
        conn = self.connect()
        
        # Example: Replace these queries with your actual SQL tables!
        # users_df = pd.read_sql("SELECT * FROM users", conn)
        # purchases_df = pd.read_sql("SELECT * FROM purchases", conn)
        
        conn.close()
        print("Raw data fetched successfully!")
        
        # return users_df, purchases_df
        return None

    def clean_and_aggregate(self):
        """Merges and cleans the data into Features and a Target."""
        # 1. Fetch data
        # users, purchases = self.fetch_raw_data()
        
        # 2. Merge tables (Example: joining users and their purchases)
        # combined_data = pd.merge(users, purchases, on="user_id")
        
        # 3. Create Features (e.g., total amount spent by user)
        # aggregated_data = combined_data.groupby('user_id').agg({
        #     'age': 'first',
        #     'purchase_amount': 'sum',
        #     'did_buy': 'last'  <-- This is your Target/Label!
        # })
        
        # 4. Save to CSV for the ML Model to train on
        # aggregated_data.to_csv('ml/training_data.csv', index=False)
        print("Data aggregated and saved to ml/training_data.csv")


if __name__ == "__main__":
    # Example config (matches your docker-compose postgres settings)
    config = {
        "url": "localhost",
        "port": 5432,
        "database": "postgres",
        "username": "postgres",
        "password": "postgres"
    }
    
    aggregator = DataAggregator(config)
    aggregator.clean_and_aggregate()
