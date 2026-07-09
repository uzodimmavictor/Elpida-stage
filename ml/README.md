# ML Local Test Data

This folder contains the offline machine learning code.

For local testing, `fake_database.sql` creates only the three panier tables used by
the aggregator:

- `paniers`
- `panier_lignes`
- `panier_ligne_option`

The schema keeps the same column names as production, but removes foreign keys to
tables that are not part of this local test, such as `produits`, `etablissements`,
and `groupe_options`.

## Load Fake Data

Start Postgres:

```bash
docker compose -f docker/docker-compose.yml up -d psql
```

Load the fake tables and rows:

```bash
docker exec -i p_container psql -U postgres -d postgres < ml/fake_database.sql
```

## Train The Model

Install Python dependencies if needed:

```bash
python3 -m pip install -r requirements.txt
```

Run the direct ML pipeline:

```bash
python3 -m ml.pipeline
```

That pipeline reads from Postgres, builds a cleaned pandas DataFrame, trains the
model, and saves it as `ml/sales_model.pkl`.
