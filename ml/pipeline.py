from ml.aggregator import DataAggregator
from ml.train import SalesModelTrainer


class SalesMLPipeline:
    def __init__(self, aggregator, trainer):
        self.aggregator = aggregator
        self.trainer = trainer

    def build_training_dataset(self):
        """Collect cleaned features directly from the aggregator."""
        return self.aggregator.get_training_data()

    def run(self):
        training_data = self.build_training_dataset()
        training_result = self.trainer.train(training_data)

        print(
            "Sales model trained from the direct pipeline. "
            f"Rows: {training_result['rows']} | "
            f"Saved to: {training_result['model_path']}"
        )
        if training_result["accuracy"] is not None:
            print(f"Test accuracy: {training_result['accuracy']:.2f}")

        return training_result


if __name__ == "__main__":
    config = {
        "url": "localhost",
        "port": 5432,
        "database": "postgres",
        "username": "postgres",
        "password": "postgres",
    }

    aggregator = DataAggregator(config)
    trainer = SalesModelTrainer()
    pipeline = SalesMLPipeline(aggregator, trainer)
    pipeline.run()
