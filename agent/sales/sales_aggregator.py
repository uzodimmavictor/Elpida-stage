from abc import ABC, abstractmethod
from aggregator import Aggregator


class SalesAggregator(Aggregator):
    
    def getData(self):
        ## database calls, cleaning
        return self.get_training_data()
        
    def __init__(self, db_config):
        self.db_config = db_config

    ## create agent for connecting to the database
    def _connect(self):
        return psycopg2.connect(
            host=self.db_config["url"],
            port=self.db_config["port"],
            database=self.db_config["database"],
            user=self.db_config["username"],
            password=self.db_config["password"],
        )

    def _fetch_raw_data(self):
        """Read the raw production-shaped tables from Postgres."""
        with self._connect() as conn:
            paniers = pd.read_sql_query("SELECT * FROM paniers", conn)
            lignes = pd.read_sql_query("SELECT * FROM panier_lignes", conn)
            options = pd.read_sql_query("SELECT * FROM panier_ligne_option", conn)

        return paniers, lignes, options

    def get_training_data(self):
        """
        Build one simple ML row per panier.

        IDs are used to parse relationships between tables. The model does not
        receive raw UUIDs; it receives useful counts and flags created from them.
        """
        paniers, lignes, options = self._fetch_raw_data()

        paniers = self._clean_paniers(paniers)
        lignes = self._clean_lignes(lignes)
        options = self._clean_options(options, lignes)

        line_totals = self._aggregate_lignes(lignes)
        option_totals = self._aggregate_options(options)

        dataset = (
            paniers.set_index("panier_id")
            .join(line_totals, how="left")
            .join(option_totals, how="left")
            .fillna(0)
            .reset_index()
        )

        return dataset

    def _clean_and_aggregate(self):
        return self.get_training_data()

    def _export_training_data_csv(self, output_path):
        """Optional helper for debugging the cleaned data by opening a CSV."""
        output_path = Path(output_path)
        data = self.get_training_data()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output_path, index=False)
        return data

    @staticmethod
    def _clean_paniers(paniers):
        paniers = paniers.copy()
        paniers = paniers.rename(columns={"id": "panier_id"})

        paniers["client_id"] = paniers["client_id"].where(
            paniers["client_id"].notna(), None
        )
        paniers["montant_total"] = pd.to_numeric(
            paniers["montant_total"], errors="coerce"
        ).fillna(0)
        paniers["remise"] = pd.to_numeric(paniers["remise"], errors="coerce").fillna(0)
        paniers["created_at"] = pd.to_datetime(paniers["created_at"], errors="coerce")
        paniers["confirmed_at"] = pd.to_datetime(
            paniers["confirmed_at"], errors="coerce"
        )

        paniers = paniers.dropna(subset=["panier_id", "created_at"])
        paniers["has_client"] = paniers["client_id"].notna().astype(int)
        paniers["is_confirmed"] = paniers["confirmed_at"].notna().astype(int)
        paniers["created_hour"] = paniers["created_at"].dt.hour
        paniers["created_day_of_week"] = paniers["created_at"].dt.dayofweek

        return paniers[
            [
                "panier_id",
                "montant_total",
                "remise",
                "created_hour",
                "created_day_of_week",
                "has_client",
                "is_confirmed",
            ]
        ]

    @staticmethod
    def _clean_lignes(lignes):
        lignes = lignes.copy()

        for column in ["parent_id", "groupe_option_id"]:
            lignes[column] = lignes[column].where(lignes[column].notna(), None)

        for column in ["quantite", "prix_unitaire", "montant", "remise", "tva"]:
            lignes[column] = pd.to_numeric(lignes[column], errors="coerce").fillna(0)

        lignes = lignes[lignes["quantite"] > 0]
        lignes["is_parent_line"] = lignes["parent_id"].isna().astype(int)
        lignes["is_child_line"] = lignes["parent_id"].notna().astype(int)
        lignes["has_option_group"] = lignes["groupe_option_id"].notna().astype(int)
        return lignes

    @staticmethod
    def _clean_options(options, lignes):
        options = options.copy()

        options["produit_id"] = options["produit_id"].where(
            options["produit_id"].notna(), None
        )
        options["groupe_option_id"] = options["groupe_option_id"].where(
            options["groupe_option_id"].notna(), None
        )

        for column in ["quantite", "supplement_unitaire", "montant_supplement"]:
            options[column] = pd.to_numeric(options[column], errors="coerce").fillna(0)

        # In this table, panier_id actually points to panier_lignes.id.
        options = options.rename(columns={"panier_id": "ligne_id"})
        line_ids = lignes[["id", "panier_id"]].rename(columns={"id": "ligne_id"})

        return options.merge(line_ids, on="ligne_id", how="inner")

    @staticmethod
    def _aggregate_lignes(lignes):
        return lignes.groupby("panier_id").agg(
            nb_lignes=("id", "count"),
            nb_lignes_parent=("is_parent_line", "sum"),
            nb_lignes_enfant=("is_child_line", "sum"),
            nb_produits_distincts=("produit_id", "nunique"),
            nb_groupes_options_lignes=("groupe_option_id", "nunique"),
            quantite_totale=("quantite", "sum"),
            montant_lignes=("montant", "sum"),
            remise_lignes=("remise", "sum"),
            tva_totale=("tva", "sum"),
        )

    @staticmethod
    def _aggregate_options(options):
        return options.groupby("panier_id").agg(
            nb_options=("id", "count"),
            nb_options_produits_distincts=("produit_id", "nunique"),
            nb_options_groupes_distincts=("groupe_option_id", "nunique"),
            montant_options=("montant_supplement", "sum"),
        )


if __name__ == "__main__":
    config = {
        "url": "localhost",
        "port": 5432,
        "database": "postgres",
        "username": "postgres",
        "password": "postgres",
    }

    aggregator = DataAggregator(config)
    data = aggregator.get_training_data()
    print(data.head())
