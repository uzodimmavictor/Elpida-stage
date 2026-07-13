from abc import ABC, abstractmethod
from pathlib import Path


class BasePipeline(ABC):
    pipeline_name = "BasePipeline"
    default_model_filename = "model.pkl"

    def __init__(self, db_connection, model_path=None):
        self.db_connection = db_connection
        self.model_path = Path(
            model_path or Path(__file__).with_name(self.default_model_filename)
        )
        self.aggregator = self.create_aggregator()
        self.trainer = self.create_trainer()

    @abstractmethod
    def create_aggregator(self):
        raise NotImplementedError

    @abstractmethod
    def create_trainer(self):
        raise NotImplementedError

    def build_training_dataset(self):
        return self.aggregator.get_training_data()

    def run(self):
        training_data = self.build_training_dataset()
        training_result = self.trainer.train(training_data)

        print(
            f"[{self.pipeline_name}] Model trained. Rows: {training_result['rows']} | "
            f"Saved to: {training_result['model_path']}"
        )
        if training_result["accuracy"] is not None:
            print(
                f"[{self.pipeline_name}] Test accuracy: {training_result['accuracy']:.2f}"
            )

        return training_result
