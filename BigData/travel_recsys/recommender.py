"""
Item-Item Collaborative Filtering — Destinations de voyage
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")


class TravelRecommender:
    def __init__(self, k_neighbors: int = 15):
        self.k = k_neighbors
        self.user_item_matrix = None
        self.item_similarity = None
        self.destinations_df = None
        self.ratings_df = None
        self._is_fitted = False

    def fit(self, ratings_df: pd.DataFrame, destinations_df: pd.DataFrame):
        self.ratings_df = ratings_df.copy()
        self.destinations_df = destinations_df.copy()

        self.user_item_matrix = ratings_df.pivot_table(
            index="userId", columns="destId", values="rating"
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

    def predict_for_profile(self, user_ratings: dict, n: int = 6) -> list:
        if not self._is_fitted or not user_ratings:
            return []

        rated_ids = set(user_ratings.keys())
        user_mean = float(np.mean(list(user_ratings.values())))

        candidates = [d for d in self.user_item_matrix.columns if d not in rated_ids]

        results = []
        for dest_id in candidates:
            if dest_id not in self.item_similarity.columns:
                continue
            sims = self.item_similarity[dest_id]
            seen_sims = {
                did: float(sims[did])
                for did in rated_ids
                if did in sims.index and sims[did] > 0
            }
            if not seen_sims:
                continue

            top_k = sorted(seen_sims.items(), key=lambda x: x[1], reverse=True)[:self.k]
            num = sum(sim * (user_ratings[did] - user_mean) for did, sim in top_k)
            den = sum(abs(sim) for _, sim in top_k)
            if den == 0:
                continue

            pred = float(np.clip(user_mean + num / den, 1.0, 5.0))
            best = top_k[:2]

            # Explication sociale
            social_str, n_users = self._social_explanation(dest_id, user_ratings)

            results.append({
                "destId": int(dest_id),
                "predicted_rating": round(pred, 2),
                "because_of": [
                    {"destId": int(did), "name": self._get_name(did), "similarity": round(float(sim), 3)}
                    for did, sim in best
                ],
                "social_explanation": social_str,
                "n_similar_users": n_users,
            })

        results.sort(key=lambda x: x["predicted_rating"], reverse=True)
        return results[:n]

    def _social_explanation(self, dest_id, user_ratings):
        rated_ids = list(user_ratings.keys())
        matches = []
        for uid in self.user_item_matrix.index:
            row = self.user_item_matrix.loc[uid]
            common = [m for m in rated_ids if m in row.index and not np.isnan(row.get(m, np.nan))]
            if len(common) < 2 or dest_id not in row.index or np.isnan(row.get(dest_id, np.nan)):
                continue
            matches.append(float(row[dest_id]))
        if not matches:
            return "", 0
        avg = round(float(np.mean(matches)), 1)
        n = len(matches)
        return f"{n} voyageur{'s' if n>1 else ''} aux goûts similaires ont noté {avg}★", n

    def get_similar_destinations(self, dest_id: int, n: int = 6) -> list:
        if dest_id not in self.item_similarity.columns:
            return []
        sims = self.item_similarity[dest_id].drop(index=dest_id, errors="ignore")
        top = sims.nlargest(n)
        return [
            {"destId": int(did), "name": self._get_name(did), "similarity": round(float(s), 3)}
            for did, s in top.items()
        ]

    def get_global_stats(self):
        return {
            "n_users": self.user_item_matrix.shape[0],
            "n_destinations": self.user_item_matrix.shape[1],
            "n_ratings": int(self.user_item_matrix.notna().sum().sum()),
            "mean_rating": round(float(self.ratings_df["rating"].mean()), 2),
        }

    def _get_name(self, dest_id):
        row = self.destinations_df[self.destinations_df["destId"] == dest_id]
        return row["name"].values[0] if len(row) else f"Dest #{dest_id}"
