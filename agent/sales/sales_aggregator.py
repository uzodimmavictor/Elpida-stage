from agent.aggregator import Aggregator

import pandas as pd


FEATURE_COLUMNS = [
    "montant_total",
    "remise",
    "created_hour",
    "created_day_of_week",
    "has_client",
    "nb_lignes",
    "nb_lignes_parent",
    "nb_lignes_enfant",
    "nb_produits_distincts",
    "nb_groupes_options_lignes",
    "quantite_totale",
    "montant_lignes",
    "remise_lignes",
    "tva_totale",
    "nb_options",
    "nb_options_produits_distincts",
    "nb_options_groupes_distincts",
    "montant_options",
]


class SalesAggregator(Aggregator):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def getData(self):
        return self.get_training_data()

    def get_training_data(self):
        paniers = pd.read_sql_query("SELECT * FROM paniers", self.db_connection)
        lignes = pd.read_sql_query("SELECT * FROM panier_lignes", self.db_connection)
        options = pd.read_sql_query("SELECT * FROM panier_ligne_option", self.db_connection)

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

    def fetch_recent_features(self):
        paniers = pd.read_sql_query(
            "SELECT id, montant_total, remise, created_at, client_id, confirmed_at "
            "FROM paniers "
            "WHERE created_at >= NOW() - INTERVAL '1 hour' "
            "ORDER BY created_at DESC LIMIT 10",
            self.db_connection,
        )
        if paniers.empty:
            return paniers

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

        lignes = pd.read_sql_query(
            "SELECT panier_id, id, parent_id, quantite, prix_unitaire, montant, remise, tva, groupe_option_id "
            "FROM panier_lignes",
            self.db_connection,
        )

        options = pd.read_sql_query(
            "SELECT panier_id, id, produit_id, groupe_option_id, quantite, supplement_unitaire, montant_supplement "
            "FROM panier_ligne_option",
            self.db_connection,
        )

        paniers["has_client"] = paniers["client_id"].notna().astype(int)
        paniers["is_confirmed"] = paniers["confirmed_at"].notna().astype(int)
        paniers["created_hour"] = paniers["created_at"].dt.hour
        paniers["created_day_of_week"] = paniers["created_at"].dt.dayofweek

        for col in ["parent_id", "groupe_option_id"]:
            lignes[col] = lignes[col].where(lignes[col].notna(), None)
        for col in ["quantite", "prix_unitaire", "montant", "remise", "tva"]:
            lignes[col] = pd.to_numeric(lignes[col], errors="coerce").fillna(0)
        lignes["is_parent_line"] = lignes["parent_id"].isna().astype(int)
        lignes["is_child_line"] = lignes["parent_id"].notna().astype(int)

        line_totals = lignes.groupby("panier_id").agg(
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

        for col in ["produit_id", "groupe_option_id"]:
            options[col] = options[col].where(options[col].notna(), None)
        for col in ["quantite", "supplement_unitaire", "montant_supplement"]:
            options[col] = pd.to_numeric(options[col], errors="coerce").fillna(0)

        option_totals = options.groupby("panier_id").agg(
            nb_options=("id", "count"),
            nb_options_produits_distincts=("produit_id", "nunique"),
            nb_options_groupes_distincts=("groupe_option_id", "nunique"),
            montant_options=("montant_supplement", "sum"),
        )

        dataset = (
            paniers.set_index("panier_id")
            .join(line_totals, how="left")
            .join(option_totals, how="left")
            .fillna(0)
            .reset_index()
        )
        return dataset[FEATURE_COLUMNS]

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
