from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

from agent.sales.sales_aggregator import FEATURE_COLUMNS

TARGET_COLUMN = "is_confirmed"


class Trainer:
    def __init__(self, model_path=None):
        self.model_path = Path(model_path or Path(__file__).with_name("sales_model.pkl"))

    def train(self, training_data):
        """Train a first supervised model from the cleaned DataFrame."""
        self.validate_training_data(training_data)

        x = training_data[FEATURE_COLUMNS]
        y = training_data[TARGET_COLUMN]

        smallest_class_count = y.value_counts().min()

        if len(training_data) < 5 or y.nunique() < 2 or smallest_class_count < 2:
            model = RandomForestClassifier(n_estimators=50, random_state=42, class_weight="balanced")
            model.fit(x, y)
            metrics = {"accuracy": None}
        else:
            x_train, x_test, y_train, y_test = train_test_split(
                x,
                y,
                test_size=0.2,
                random_state=42,
                stratify=y,
            )

            model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
            model.fit(x_train, y_train)
            predictions = model.predict(x_test)
            metrics = {
                "accuracy": accuracy_score(y_test, predictions),
                "precision": precision_score(y_test, predictions, zero_division=0),
                "recall": recall_score(y_test, predictions, zero_division=0),
                "f1": f1_score(y_test, predictions, zero_division=0),
            }

        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, self.model_path)

        importances = dict(zip(FEATURE_COLUMNS, map(float, model.feature_importances_)))

        print(f"[Trainer] Metrics: {metrics}")
        print(f"[Trainer] Top 5 features: {sorted(importances, key=importances.get, reverse=True)[:5]}")

        return {
            "model": model,
            "model_path": self.model_path,
            "metrics": metrics,
            "rows": len(training_data),
            "features": FEATURE_COLUMNS,
            "target": TARGET_COLUMN,
            "feature_importances": importances,
        }

    @staticmethod
    def validate_training_data(training_data):
        missing_columns = [
            column
            for column in [*FEATURE_COLUMNS, TARGET_COLUMN]
            if column not in training_data.columns
        ]

        if missing_columns:
            raise ValueError(f"Training data is missing columns: {missing_columns}")

        if training_data.empty:
            raise ValueError("Training data is empty.")
