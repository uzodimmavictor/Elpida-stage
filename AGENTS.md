# Elpida-stage

Custom Python DI framework with event-driven agent components, Kafka messaging, Redis caching, and scikit-learn ML inference.

## Entrypoints

- **App:** `python main.py config.json [--start]` — bootstraps all components via DI, enters sleep loop until Ctrl+C
- **ML training (standalone):** `python agent/sales/pipeline.py` — connects directly to Postgres, runs aggregator + trainer, writes `sales_model.pkl`

## Architecture

**Custom DI framework** (no third-party lib): `context.py` singleton reads `config.json`, instantiates components via `component_registry.REGISTRY` + `factory()`, then applies configs and wires dependencies.

**Lifecycle order** (`context.start()`):
1. `connect()` — for components that have it (DBs, Kafka)
2. `onEnterLoopBefore()` — resolve deps, load model, subscribe to Kafka topics
3. `onEnterLoop()` — start background threads (KafkaConsumer poll, AgentSales loop, HTTP server)
4. `onEnterLoopAfter()` — post-startup checks

**Shutdown:** `context.stop()` calls `disconnect()` in reverse order.

## Components (7 total, mirrors `config.json`)

| Config key | Registry key | Class | File |
|---|---|---|---|
| `Influx` | `Influx` | `InfluxDB` | `database/influx.py` |
| `Redis` | `Redis` | `RedisDB` | `database/redis.py` |
| `Postgres` | `Postgres` | `PostgresDB` | `database/postgres.py` |
| `KafkaProducer` | `KafkaProducer` | `KafkaProducer` | `messaging/kafka_producer.py` |
| `KafkaConsumer` | `KafkaConsumer` | `KafkaConsumer` | `messaging/kafka_consumer.py` |
| `AgentSales` | `AgentSales` | `AgentSales` | `agent/sales/sales.py` |
| `RestAPI` | `RestAPI` | `RestAPI` | `api/rest_api.py` |

**Bootstrap:** `package/component_descriptor.py` must import every concrete component to trigger `@registry(...)` decoration. The `package/__init__.py` does this on import.

## Registration pattern

```python
@registry("ComponentName")
class SomeComponent(Component):
    dependencies = [Dependency[SomeType]("dep_name", SomeType), ...]
```

`Dependency[T]` name must match the key in `config.json`'s `Dependencies` section.

## Known issues

- `api/handler.py` has dead code: `_send` and `log_message` are indented inside `do_GET` after `return` (unreachable)
- `api/get_sales_suggestions.py` references `Context.get_component()` which does not exist — placeholder
- `api/rest_handler.py` uses `@abstractmethod` without inheriting `ABC`
- `sales_model.pkl` is checked into git (trained artifact)
- No lockfile (`requirements.txt` only), builds not reproducible
- No tests, no CI, no linting, no typechecking configured

## Infrastructure

```
docker compose up -d    # starts Postgres 17, InfluxDB 1.8.3, Redis 7, Kafka (KRaft)
```

Seed data: `database/fake_database.sql` mounts into Postgres container via `docker-compose.yml`.

## ML pipeline

- **Aggregator:** `SalesAggregator` queries `paniers`, `panier_lignes`, `panier_ligne_option`, joins into feature DataFrame (18 numeric features, `is_confirmed` target)
- **Trainer:** `RandomForestClassifier` (50 or 100 estimators), saves to `sales_model.pkl` via joblib
- **Base class:** `agent/base_pipeline.py` — template for future agent pipelines
- **Runtime:** `AgentSales` loads model in `onEnterLoopBefore()`, runs inference every `period` seconds (default 900), publishes one message per establishment to `sales-suggestions` Kafka topic
- **Per-establishment:** `build_sales_suggestions()` groups `fetch_recent_features()` by `enseigne_id`, runs `predict()` per group, returns a list with one suggestion dict per establishment. Each dict includes `"enseigne_id"`. API accepts `?enseigne_id=` query param to filter.

## Key patterns

- Components declare dependencies via class-level `dependencies = [Dependency[...](...)]`. Injected by name from `config.json["Dependencies"]`.
- `getDependency(name, Type)` enforces type at runtime.
- `SuggestionService` wraps Redis get/set with double-checked locking and TTL expiry.
- Kafka events flow: topic → `KafkaConsumer._poll()` → `handler.eventReceived(topic, data)`. Components implement `eventReceived()` to react.
- `AgentSales.eventReceived()` handles `sales_suggestion_request` and `retrain_requested` event types.
