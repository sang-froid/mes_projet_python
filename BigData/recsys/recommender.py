"""
Item-Item Collaborative Filtering Engine
Système de recommandation basé sur la similarité cosinus entre items.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings("ignore")


class ItemItemRecommender:
    """
    Filtrage collaboratif item-item avec similarité cosinus.

    Pipeline:
    1. Construire la matrice utilisateur-item (ratings)
    2. Centrer les notes par utilisateur (mean-centered)
    3. Calculer la similarité cosinus entre tous les items
    4. Prédire la note d'un item pour un utilisateur via agrégation pondérée
    5. Retourner le Top-N items recommandés
    """

    def __init__(self, k_neighbors: int = 20):
        self.k = k_neighbors
        self.user_item_matrix = None
        self.item_similarity = None
        self.movies_df = None
        self.ratings_df = None
        self.mean_ratings = None
        self.centered_matrix = None
        self._is_fitted = False

    # ------------------------------------------------------------------
    # Fit
    # ------------------------------------------------------------------

    def fit(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame):
        """Entraîne le modèle sur les données de ratings."""
        self.ratings_df = ratings_df.copy()
        self.movies_df = movies_df.copy()

        # Matrice utilisateur-item (lignes = users, colonnes = items)
        self.user_item_matrix = ratings_df.pivot_table(
            index="userId", columns="movieId", values="rating"
        )

        # Centrage par utilisateur (soustraction de la moyenne)
        self.mean_ratings = self.user_item_matrix.mean(axis=1)
        self.centered_matrix = self.user_item_matrix.sub(self.mean_ratings, axis=0).fillna(0)

        # Similarité cosinus entre items  (transposée : items en lignes)
        item_vectors = self.centered_matrix.T.values
        sim_matrix = cosine_similarity(item_vectors)

        self.item_similarity = pd.DataFrame(
            sim_matrix,
            index=self.user_item_matrix.columns,
            columns=self.user_item_matrix.columns,
        )

        self._is_fitted = True
        return self

    # ------------------------------------------------------------------
    # Prédiction d'une note
    # ------------------------------------------------------------------

    def predict_rating(self, user_id: int, movie_id: int) -> dict:
        """
        Prédit la note qu'un utilisateur donnerait à un film.
        
        Formule (Sarwar et al., 2001) :
            pred(u, i) = mean(u) + Σ sim(i,j) * (r(u,j) - mean(u))
                                   ─────────────────────────────────
                                        Σ |sim(i,j)|
        """
        if not self._is_fitted:
            raise RuntimeError("Le modèle n'est pas encore entraîné.")

        if movie_id not in self.user_item_matrix.columns:
            return {"error": "Film inconnu dans le modèle."}

        if user_id not in self.user_item_matrix.index:
            return {"error": "Utilisateur inconnu dans le modèle."}

        # Notes déjà données par l'utilisateur
        user_ratings = self.user_item_matrix.loc[user_id].dropna()

        # Similarités du film cible avec tous les films notés par l'user
        sims = self.item_similarity[movie_id]
        rated_sims = sims[user_ratings.index].drop(index=movie_id, errors="ignore")

        # Sélection des k meilleurs voisins (similarité positive)
        top_sims = rated_sims[rated_sims > 0].nlargest(self.k)

        if top_sims.empty:
            # Fallback : moyenne globale du film
            movie_mean = self.user_item_matrix[movie_id].mean()
            return {
                "prediction": round(float(movie_mean), 2),
                "method": "fallback_mean",
                "n_neighbors": 0,
                "neighbors": [],
            }

        user_mean = self.mean_ratings[user_id]
        neighbor_ratings = user_ratings[top_sims.index]
        centered_neighbor = neighbor_ratings - user_mean

        numerator = (top_sims * centered_neighbor).sum()
        denominator = top_sims.abs().sum()

        prediction = user_mean + (numerator / denominator)
        prediction = float(np.clip(prediction, 1.0, 5.0))

        neighbors_info = []
        for mid, sim in top_sims.items():
            title = self._get_title(mid)
            neighbors_info.append({
                "movieId": int(mid),
                "title": title,
                "similarity": round(float(sim), 4),
                "user_rating": round(float(user_ratings[mid]), 1),
            })

        return {
            "prediction": round(prediction, 2),
            "method": "item_item_cf",
            "n_neighbors": len(top_sims),
            "neighbors": neighbors_info,
            "user_mean": round(float(user_mean), 2),
        }

    # ------------------------------------------------------------------
    # Top-N recommandations
    # ------------------------------------------------------------------

    def recommend_top_n(self, user_id: int, n: int = 10) -> pd.DataFrame:
        """
        Retourne les N films les mieux notés que l'utilisateur n'a pas encore vus.
        """
        if not self._is_fitted:
            raise RuntimeError("Le modèle n'est pas encore entraîné.")

        if user_id not in self.user_item_matrix.index:
            return pd.DataFrame()

        # Films déjà notés
        already_rated = self.user_item_matrix.loc[user_id].dropna().index.tolist()

        # Films candidats
        candidates = [
            mid for mid in self.user_item_matrix.columns
            if mid not in already_rated
        ]

        results = []
        for movie_id in candidates:
            pred = self.predict_rating(user_id, movie_id)
            if "error" not in pred:
                results.append({
                    "movieId": movie_id,
                    "title": self._get_title(movie_id),
                    "genres": self._get_genres(movie_id),
                    "predicted_rating": pred["prediction"],
                    "n_neighbors": pred["n_neighbors"],
                })

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results).sort_values("predicted_rating", ascending=False)
        return df.head(n).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Similarité entre items
    # ------------------------------------------------------------------

    def get_similar_items(self, movie_id: int, n: int = 10) -> pd.DataFrame:
        """Retourne les N films les plus similaires à un film donné."""
        if movie_id not in self.item_similarity.columns:
            return pd.DataFrame()

        sims = self.item_similarity[movie_id].drop(index=movie_id, errors="ignore")
        top = sims.nlargest(n)

        rows = []
        for mid, sim in top.items():
            rows.append({
                "movieId": int(mid),
                "title": self._get_title(mid),
                "genres": self._get_genres(mid),
                "similarity": round(float(sim), 4),
            })
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Matrice de similarité (pour visualisation heatmap)
    # ------------------------------------------------------------------

    def get_similarity_submatrix(self, movie_ids: list) -> pd.DataFrame:
        """Retourne la sous-matrice de similarité pour une liste de films."""
        valid = [m for m in movie_ids if m in self.item_similarity.columns]
        titles = {m: self._get_title(m) for m in valid}
        sub = self.item_similarity.loc[valid, valid]
        sub.index = [titles[m] for m in valid]
        sub.columns = [titles[m] for m in valid]
        return sub

    # ------------------------------------------------------------------
    # Statistiques & utilitaires
    # ------------------------------------------------------------------

    def get_user_stats(self, user_id: int) -> dict:
        if user_id not in self.user_item_matrix.index:
            return {}
        user_row = self.user_item_matrix.loc[user_id].dropna()
        return {
            "n_ratings": len(user_row),
            "mean_rating": round(float(user_row.mean()), 2),
            "min_rating": float(user_row.min()),
            "max_rating": float(user_row.max()),
            "rated_movies": user_row.sort_values(ascending=False),
        }

    def get_movie_stats(self, movie_id: int) -> dict:
        if movie_id not in self.user_item_matrix.columns:
            return {}
        col = self.user_item_matrix[movie_id].dropna()
        return {
            "n_ratings": len(col),
            "mean_rating": round(float(col.mean()), 2),
            "std_rating": round(float(col.std()), 2),
        }

    def get_all_movies(self) -> pd.DataFrame:
        return self.movies_df.copy()

    def get_all_users(self) -> list:
        return sorted(self.user_item_matrix.index.tolist())

    def get_sparsity(self) -> float:
        total = self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]
        filled = self.user_item_matrix.notna().sum().sum()
        return round(1 - filled / total, 4)

    def _get_title(self, movie_id: int) -> str:
        row = self.movies_df[self.movies_df["movieId"] == movie_id]
        return row["title"].values[0] if len(row) else f"Film #{movie_id}"

    def _get_genres(self, movie_id: int) -> str:
        row = self.movies_df[self.movies_df["movieId"] == movie_id]
        return row["genres"].values[0] if len(row) else ""
