"""
Item-Item Collaborative Filtering Engine
Le système prend le profil de notes d'un nouvel utilisateur,
calcule les prédictions et explique pourquoi chaque film est recommandé.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")


class ItemItemRecommender:
    def __init__(self, k_neighbors: int = 20):
        self.k = k_neighbors
        self.user_item_matrix = None
        self.item_similarity = None
        self.movies_df = None
        self.ratings_df = None
        self.mean_ratings = None
        self._is_fitted = False

    def fit(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame):
        self.ratings_df = ratings_df.copy()
        self.movies_df = movies_df.copy()

        self.user_item_matrix = ratings_df.pivot_table(
            index="userId", columns="movieId", values="rating"
        )
        self.mean_ratings = self.user_item_matrix.mean(axis=1)
        centered = self.user_item_matrix.sub(self.mean_ratings, axis=0).fillna(0)

        sim_matrix = cosine_similarity(centered.T.values)
        self.item_similarity = pd.DataFrame(
            sim_matrix,
            index=self.user_item_matrix.columns,
            columns=self.user_item_matrix.columns,
        )
        self._is_fitted = True
        return self

    def predict_for_user_profile(self, user_ratings: dict, n: int = 10) -> list:
        """
        user_ratings : {movie_id: rating}
        Retourne Top-N films non vus avec prédiction + double explication.
        """
        if not self._is_fitted or not user_ratings:
            return []

        rated_ids = set(user_ratings.keys())
        user_mean = float(np.mean(list(user_ratings.values())))

        candidates = [
            mid for mid in self.user_item_matrix.columns
            if mid not in rated_ids
        ]

        results = []
        for movie_id in candidates:
            if movie_id not in self.item_similarity.columns:
                continue

            sims = self.item_similarity[movie_id]
            seen_sims = {
                mid: float(sims[mid])
                for mid in rated_ids
                if mid in sims.index and sims[mid] > 0
            }
            if not seen_sims:
                continue

            top_k = sorted(seen_sims.items(), key=lambda x: x[1], reverse=True)[: self.k]
            num = sum(sim * (user_ratings[mid] - user_mean) for mid, sim in top_k)
            den = sum(abs(sim) for _, sim in top_k)
            if den == 0:
                continue

            pred = float(np.clip(user_mean + num / den, 1.0, 5.0))

            best_seen = top_k[:3]
            expl_item = self._build_item_explanation(best_seen, user_ratings)
            expl_user, sim_users = self._build_user_explanation(movie_id, user_ratings)

            results.append({
                "movieId": int(movie_id),
                "title": self._get_title(movie_id),
                "genres": self._get_genres(movie_id),
                "predicted_rating": round(pred, 2),
                "n_neighbors": len(top_k),
                "top_similar_seen": [
                    {
                        "movieId": int(mid),
                        "title": self._get_title(mid),
                        "similarity": round(float(sim), 3),
                        "your_rating": user_ratings[mid],
                    }
                    for mid, sim in best_seen
                ],
                "explanation_item": expl_item,
                "explanation_user": expl_user,
                "similar_users_info": sim_users,
            })

        results.sort(key=lambda x: x["predicted_rating"], reverse=True)
        return results[:n]

    def _build_item_explanation(self, top_k_seen, user_ratings):
        parts = []
        for mid, sim in top_k_seen[:2]:
            title = self._get_title(mid)
            r = user_ratings[mid]
            sentiment = "adoré" if r >= 4.5 else ("bien aimé" if r >= 3.5 else "vu")
            parts.append((title, sim, r, sentiment))
        if not parts:
            return ""
        if len(parts) == 1:
            t, s, r, sent = parts[0]
            return f"Très similaire à **{t}** que tu as {sent} ({r}★, sim. {s:.2f})"
        (t1, s1, r1, sent1), (t2, s2, r2, sent2) = parts
        return (
            f"Similaire à **{t1}** (tu as {sent1} · {r1}★) "
            f"et **{t2}** (tu as {sent2} · {r2}★)"
        )

    def _build_user_explanation(self, movie_id: int, user_ratings: dict):
        rated_ids = list(user_ratings.keys())
        candidates_users = []

        for uid in self.user_item_matrix.index:
            row = self.user_item_matrix.loc[uid]
            common = [m for m in rated_ids if m in row.index and not np.isnan(row.get(m, np.nan))]
            if len(common) < 2:
                continue
            if movie_id not in row.index or np.isnan(row.get(movie_id, np.nan)):
                continue

            vec_new = np.array([user_ratings[m] for m in common], dtype=float)
            vec_db = np.array([row[m] for m in common], dtype=float)
            norm_new = np.linalg.norm(vec_new)
            norm_db = np.linalg.norm(vec_db)
            if norm_new == 0 or norm_db == 0:
                continue

            sim = float(np.dot(vec_new, vec_db) / (norm_new * norm_db))
            candidates_users.append({
                "userId": uid,
                "similarity": round(sim, 3),
                "their_rating": round(float(row[movie_id]), 1),
                "common_titles": [self._get_title(m) for m in common[:3]],
                "n_common": len(common),
            })

        if not candidates_users:
            return "", []

        candidates_users.sort(key=lambda x: x["similarity"], reverse=True)
        top_users = candidates_users[:6]
        avg_rating = round(float(np.mean([u["their_rating"] for u in top_users])), 2)
        n = len(top_users)

        all_titles = []
        for u in top_users[:3]:
            all_titles += u["common_titles"]
        rep = list(dict.fromkeys(all_titles))[:3]
        rep_str = " et ".join(f"**{t}**" for t in rep)

        expl = (
            f"{n} utilisateur{'s' if n > 1 else ''} qui ont aussi aimé {rep_str} "
            f"ont donné en moyenne **{avg_rating}★** à ce film"
        )
        return expl, top_users

    def get_similar_items(self, movie_id: int, n: int = 8) -> pd.DataFrame:
        if movie_id not in self.item_similarity.columns:
            return pd.DataFrame()
        sims = self.item_similarity[movie_id].drop(index=movie_id, errors="ignore")
        top = sims.nlargest(n)
        return pd.DataFrame([
            {"movieId": int(m), "title": self._get_title(m),
             "genres": self._get_genres(m), "similarity": round(float(s), 4)}
            for m, s in top.items()
        ])

    def get_similarity_submatrix(self, movie_ids: list) -> pd.DataFrame:
        valid = [m for m in movie_ids if m in self.item_similarity.columns]
        titles = {m: self._get_title(m) for m in valid}
        sub = self.item_similarity.loc[valid, valid].copy()
        sub.index = [titles[m] for m in valid]
        sub.columns = [titles[m] for m in valid]
        return sub

    def get_all_movies(self) -> pd.DataFrame:
        return self.movies_df.copy()

    def get_global_stats(self) -> dict:
        return {
            "n_users": self.user_item_matrix.shape[0],
            "n_movies": self.user_item_matrix.shape[1],
            "n_ratings": int(self.user_item_matrix.notna().sum().sum()),
            "mean_rating": round(float(self.ratings_df["rating"].mean()), 2),
            "sparsity": round(1 - self.user_item_matrix.notna().sum().sum() /
                              (self.user_item_matrix.shape[0] * self.user_item_matrix.shape[1]), 4),
        }

    def _get_title(self, movie_id: int) -> str:
        row = self.movies_df[self.movies_df["movieId"] == movie_id]
        return row["title"].values[0] if len(row) else f"Film #{movie_id}"

    def _get_genres(self, movie_id: int) -> str:
        row = self.movies_df[self.movies_df["movieId"] == movie_id]
        return row["genres"].values[0] if len(row) else ""
