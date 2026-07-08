# Agent Handoff Document

Hello next AI Agent! You are assisting a software engineering intern ("a total beginner") in building a dynamic Component-based Python framework.

## 1. Project Architecture (Elpida-stage)
This is a custom Python framework heavily relying on Dependency Injection driven by a JSON config.
- `main.py`: Entry point. Keeps the main thread alive so background component threads can run.
- `config.json`: The blueprint. Defines which components to instantiate, their config (credentials), and their dependencies (e.g., mapping `postgres` to `AgentSales`).
- `context.py`: The "Motherboard". Parses `config.json`, uses a Factory to instantiate classes, calls `configure()`, resolves and injects `Dependencies` via `setDependency()`.
- **Lifecycle:** `context.start()` calls the following in order on all components:
  1. `onEnterLoopBefore()`: Initial setup (e.g., fetching injected dependencies).
  2. `onEnterLoop()`: Start background tasks (e.g., spinning up a `threading.Thread`).
  3. `onEnterLoopAfter()`: Post-loop setup (e.g., Databases establish connection here).

## 2. What Has Been Completed So Far
- Fixed dynamic dependency injection logic (`Context.apply_dependencies`).
- Enforced strict type-checking in `Component.setDependency`.
- Implemented Database components (`InfluxDB`, `RedisDB`, `PostgresDB`).
- Created the first agent component: `AgentSales` (`agent/sales.py`). It correctly requests `PostgresDB`, receives it, and runs a background `threading.Thread` doing mock tasks.
- Created educational artifacts for the user: `project_explanation.md` and `ml_integration_guide.md`.

## 3. The Current Mission: Machine Learning Integration
The tutor wants `AgentSales` to become an AI agent. It needs to generate predictions based on a Supervised Learning ML model and push those results to Kafka.

### Folder Structure Setup:
We created an `ml/` directory to separate ML logic from the live agent framework:
- `ml/aggregator.py` (Skeleton created): Standalone script to pull fake SQL data via `psycopg2` and `pandas`, clean it, and export `training_data.csv`.

## 4. Next Steps / Action Items for the Next Agent
1. **The Aggregator**: The user is waiting on a fake SQL file from their tutor. Once they have it, help them write `pandas` logic in `ml/aggregator.py` to join tables, extract features, define a Target/Label, and save to CSV.
2. **Model Training**: Create `ml/train.py`. Write a script to load the CSV, train a simple `scikit-learn` model (e.g., `RandomForestClassifier`), and export it as `sales_model.pkl` (using `joblib`).
3. **Inference Setup**: Modify `agent/sales.py` to load `sales_model.pkl` in `onEnterLoopBefore()`. Inside its background thread loop, use the model to make predictions.
4. **Kafka Integration**: Create a brand new Component called `KafkaProducer` (using `kafka-python`). Register it in `config.json` and inject it into `AgentSales`. Update `AgentSales` to publish its predictions to a Kafka topic!

**Note on User Skill Level:** The user is a beginner. Provide detailed explanations, avoid heavy jargon, and explain *why* you are doing something before providing the code. Use analogies where possible!
