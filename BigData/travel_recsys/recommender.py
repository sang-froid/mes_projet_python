"""
recommender.py
══════════════════════════════════════════════════════════════════════════════
Algorithme de recommandation : Filtrage Collaboratif Item-Item
──────────────────────────────────────────────────────────────────────────────
Principe :
  1. On construit une matrice Utilisateurs × Destinations (notes 1-5).
  2. On calcule la similarité cosinus entre chaque paire de destinations
     (à partir des profils de notes centrés sur la moyenne de chaque user).
  3. Pour prédire la note d'un utilisateur sur une destination inconnue,
     on fait une moyenne pondérée des notes qu'il a déjà données,
     pondérée par la similarité entre chaque destination notée et la cible.
══════════════════════════════════════════════════════════════════════════════
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore")


class TravelRecommender:
    """
    Moteur de recommandation de destinations de voyage.
    Utilise le filtrage collaboratif item-item avec similarité cosinus.
    """

    def __init__(self, k_neighbors: int = 15):
        """
        Initialise le modèle.

        Paramètre :
            k_neighbors : nombre maximum de destinations "voisines" (similaires)
                          utilisées pour calculer une prédiction.
                          Plus k est grand, plus la prédiction est lissée.
        """
        self.k = k_neighbors

        # Matrice pivot : lignes = users, colonnes = destinations, valeurs = notes
        self.user_item_matrix = None

        # Matrice carrée destinations × destinations : contient les scores de similarité
        self.item_similarity = None

        # DataFrames bruts conservés pour les lookups (noms, stats, etc.)
        self.destinations_df = None
        self.ratings_df = None

        # Flag : True seulement après appel à fit()
        self._is_fitted = False

    # ──────────────────────────────────────────────────────────────────────
    # ENTRAÎNEMENT
    # ──────────────────────────────────────────────────────────────────────

    def fit(self, ratings_df: pd.DataFrame, destinations_df: pd.DataFrame):
        """
        Entraîne le modèle à partir des données de notes et de destinations.

        Étapes :
          1. Construction de la matrice user-item (pivot table).
          2. Centrage des notes par utilisateur (soustraction de la moyenne)
             → permet de neutraliser les biais individuels (un user qui note
               toujours 5 vs un user qui note toujours 2).
          3. Calcul de la similarité cosinus entre toutes les paires de destinations
             à partir des vecteurs de notes centrés.

        Retourne self pour permettre le chaînage : model.fit(...).predict(...)
        """
        # Sauvegarde des données brutes pour usage ultérieur
        self.ratings_df = ratings_df.copy()
        self.destinations_df = destinations_df.copy()

        # ── Étape 1 : Matrice user × item ──────────────────────────────────
        # Chaque cellule contient la note donnée par un user à une destination.
        # Les cellules vides (destination non notée) restent à NaN.
        self.user_item_matrix = ratings_df.pivot_table(
            index="userId", columns="destId", values="rating"
        )

        # ── Étape 2 : Centrage des notes ───────────────────────────────────
        # On calcule la note moyenne de chaque utilisateur (sur toutes ses notes).
        self.mean_ratings = self.user_item_matrix.mean(axis=1)

        # On soustrait la moyenne de chaque ligne (user), puis on remplace
        # les NaN par 0 (destination non notée = note neutre après centrage).
        centered = self.user_item_matrix.sub(self.mean_ratings, axis=0).fillna(0)

        # ── Étape 3 : Similarité cosinus entre destinations ────────────────
        # On transpose la matrice (destinations en lignes) puis on calcule
        # la similarité cosinus entre chaque paire de destinations.
        # Résultat : matrice carré n_destinations × n_destinations.
        # Valeur ∈ [-1, 1] : 1 = identiques, 0 = indépendantes, -1 = opposées.
        sim_matrix = cosine_similarity(centered.T.values)

        # Conversion en DataFrame pour faciliter les lookups par destId
        self.item_similarity = pd.DataFrame(
            sim_matrix,
            index=self.user_item_matrix.columns,
            columns=self.user_item_matrix.columns,
        )

        self._is_fitted = True
        return self

    # ──────────────────────────────────────────────────────────────────────
    # PRÉDICTION POUR UN PROFIL UTILISATEUR
    # ──────────────────────────────────────────────────────────────────────

    def predict_for_profile(self, user_ratings: dict, n: int = 6) -> list:
        """
        Génère les n meilleures recommandations pour un utilisateur défini
        par ses notes (profil manuel, pas nécessairement dans le dataset).

        Paramètres :
            user_ratings : dict {destId: note} — destinations déjà notées
            n            : nombre de recommandations à retourner

        Retourne :
            Liste de dicts triée par score prédit décroissant, chacun contenant :
              - destId            : identifiant de la destination recommandée
              - predicted_rating  : note prédite (entre 1.0 et 5.0)
              - because_of        : les 2 destinations similaires qui ont le plus
                                    influencé la prédiction (pour l'explication)
              - social_explanation: phrase résumant les avis d'autres voyageurs
              - n_similar_users   : nombre de voyageurs similaires trouvés
        """
        if not self._is_fitted or not user_ratings:
            return []

        # Destinations déjà notées par l'utilisateur → à exclure des recommandations
        rated_ids = set(user_ratings.keys())

        # Moyenne des notes de l'utilisateur (utilisée pour le centrage dans la formule)
        user_mean = float(np.mean(list(user_ratings.values())))

        # Destinations candidates = toutes celles du dataset NON encore notées
        candidates = [d for d in self.user_item_matrix.columns if d not in rated_ids]

        results = []
        for dest_id in candidates:

            # Vérification que la destination est bien dans la matrice de similarité
            if dest_id not in self.item_similarity.columns:
                continue

            # Récupère le vecteur de similarité de cette destination
            # avec toutes les autres
            sims = self.item_similarity[dest_id]

            # Ne garde que les destinations déjà notées par l'user
            # et dont la similarité est positive (influencerait positivement)
            seen_sims = {
                did: float(sims[did])
                for did in rated_ids
                if did in sims.index and sims[did] > 0
            }

            # Si aucune destination notée n'est similaire, on ne peut pas prédire
            if not seen_sims:
                continue

            # Sélection des k voisins les plus similaires (top-k)
            top_k = sorted(seen_sims.items(), key=lambda x: x[1], reverse=True)[:self.k]

            # ── Formule de prédiction item-item ────────────────────────────
            # pred = moyenne_user + Σ(sim_ij × (note_j - moyenne_user)) / Σ|sim_ij|
            #
            # → On ajuste la moyenne de l'user par une correction pondérée :
            #   si les destinations similaires ont été notées AU-DESSUS de
            #   sa moyenne, on prédit une note élevée, et inversement.
            num = sum(sim * (user_ratings[did] - user_mean) for did, sim in top_k)
            den = sum(abs(sim) for _, sim in top_k)

            if den == 0:
                continue  # Évite la division par zéro

            # Clip pour rester dans l'intervalle valide [1.0, 5.0]
            pred = float(np.clip(user_mean + num / den, 1.0, 5.0))

            # Les 2 destinations les plus similaires → utilisées pour l'explication UI
            best = top_k[:2]

            # Génération de l'explication sociale (combien de vrais users ont aimé ça)
            social_str, n_users = self._social_explanation(dest_id, user_ratings)

            results.append({
                "destId": int(dest_id),
                "predicted_rating": round(pred, 2),
                "because_of": [
                    {
                        "destId": int(did),
                        "name": self._get_name(did),
                        "similarity": round(float(sim), 3)
                    }
                    for did, sim in best
                ],
                "social_explanation": social_str,
                "n_similar_users": n_users,
            })

        # Tri par score prédit décroissant, retour des n meilleurs
        results.sort(key=lambda x: x["predicted_rating"], reverse=True)
        return results[:n]

    # ──────────────────────────────────────────────────────────────────────
    # EXPLICATION SOCIALE
    # ──────────────────────────────────────────────────────────────────────

    def _social_explanation(self, dest_id, user_ratings):
        """
        Cherche dans le dataset les utilisateurs réels qui ont :
          - noté au moins 2 destinations en commun avec l'utilisateur courant
          - noté la destination cible (dest_id)

        Ces utilisateurs sont considérés comme "aux goûts similaires".
        On retourne la note moyenne qu'ils ont donnée à dest_id,
        ainsi que leur nombre, sous forme de phrase lisible.

        Paramètres :
            dest_id      : destination pour laquelle on génère l'explication
            user_ratings : dict {destId: note} du profil courant

        Retourne :
            (phrase: str, n_users: int)
        """
        rated_ids = list(user_ratings.keys())
        matches = []

        for uid in self.user_item_matrix.index:
            row = self.user_item_matrix.loc[uid]

            # Compte les destinations communes notées par cet utilisateur réel
            common = [
                m for m in rated_ids
                if m in row.index and not np.isnan(row.get(m, np.nan))
            ]

            # On exige au moins 2 destinations en commun (profil suffisamment proche)
            # et que cet utilisateur ait aussi noté la destination cible
            if len(common) < 2 or dest_id not in row.index or np.isnan(row.get(dest_id, np.nan)):
                continue

            matches.append(float(row[dest_id]))

        if not matches:
            return "", 0  # Pas assez de données pour une explication sociale

        avg = round(float(np.mean(matches)), 1)
        n = len(matches)

        # Phrase affichée dans l'interface
        return f"{n} voyageur{'s' if n > 1 else ''} aux goûts similaires ont noté {avg}★", n

    # ──────────────────────────────────────────────────────────────────────
    # DESTINATIONS SIMILAIRES (page Similarité)
    # ──────────────────────────────────────────────────────────────────────

    def get_similar_destinations(self, dest_id: int, n: int = 6) -> list:
        """
        Retourne les n destinations les plus similaires à dest_id,
        selon la matrice de similarité cosinus calculée à l'entraînement.

        Utilisé dans la page "Similarité" de l'interface.

        Paramètres :
            dest_id : identifiant de la destination de référence
            n       : nombre de destinations similaires à retourner

        Retourne :
            Liste de dicts [{destId, name, similarity}] triée par similarité décroissante
        """
        if dest_id not in self.item_similarity.columns:
            return []  # Destination inconnue du modèle

        # Récupère la colonne de similarité et retire la destination elle-même (sim = 1.0)
        sims = self.item_similarity[dest_id].drop(index=dest_id, errors="ignore")

        # Sélection des n plus grandes similarités
        top = sims.nlargest(n)

        return [
            {
                "destId": int(did),
                "name": self._get_name(did),
                "similarity": round(float(s), 3)
            }
            for did, s in top.items()
        ]

    # ──────────────────────────────────────────────────────────────────────
    # STATISTIQUES GLOBALES (affichées dans la sidebar)
    # ──────────────────────────────────────────────────────────────────────

    def get_global_stats(self):
        """
        Retourne des statistiques descriptives sur le dataset chargé.
        Utilisé pour alimenter les métriques affichées dans la sidebar.

        Retourne un dict avec :
            n_users        : nombre d'utilisateurs uniques
            n_destinations : nombre de destinations uniques
            n_ratings      : nombre total de notes (cellules non-NaN)
            mean_rating    : note moyenne globale sur tout le dataset
        """
        return {
            "n_users":        self.user_item_matrix.shape[0],
            "n_destinations": self.user_item_matrix.shape[1],
            # .notna().sum().sum() compte toutes les cellules non-vides
            "n_ratings":      int(self.user_item_matrix.notna().sum().sum()),
            "mean_rating":    round(float(self.ratings_df["rating"].mean()), 2),
        }

    # ──────────────────────────────────────────────────────────────────────
    # UTILITAIRE INTERNE
    # ──────────────────────────────────────────────────────────────────────

    def _get_name(self, dest_id):
        """
        Retourne le nom d'une destination à partir de son identifiant.
        Utilisé pour enrichir les résultats avec des noms lisibles.

        Si la destination n'est pas trouvée dans le DataFrame,
        retourne un nom de fallback générique.
        """
        row = self.destinations_df[self.destinations_df["destId"] == dest_id]
        return row["name"].values[0] if len(row) else f"Dest #{dest_id}"