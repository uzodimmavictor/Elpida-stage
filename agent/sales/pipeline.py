from database.postgres import PostgresDB

from agent.base_pipeline import BasePipeline
from agent.sales.sales_aggregator import SalesAggregator
from agent.sales.train import Trainer


class SalesPipeline(BasePipeline):
    pipeline_name = "SalesPipeline"
    default_model_filename = "sales_model.pkl"

    def create_aggregator(self):
        return SalesAggregator(self.db_connection)

    def create_trainer(self):
        return Trainer(str(self.model_path))


if __name__ == "__main__":
    config = {
        "url": "localhost",
        "port": 5432,
        "database": "postgres",
        "username": "postgres",
        "password": "postgres",
    }

    db = PostgresDB("PostgresDB", True)
    db.configure(config)
    db.connect()

    pipeline = SalesPipeline(db.connection)
    pipeline.run()
