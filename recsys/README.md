# CineMatch — Système de Recommandation Item-Item

TP1 · Filtrage Collaboratif · MovieLens · Streamlit

## Lancer l'application

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer Streamlit
streamlit run app.py
```

L'app s'ouvre automatiquement sur http://localhost:8501

## Structure du projet

```
recsys/
├── app.py              # Interface Streamlit (4 pages)
├── recommender.py      # Moteur Item-Item CF
├── requirements.txt
└── data/
    ├── movies.csv      # Catalogue films (id, titre, genres)
    └── ratings.csv     # Notes utilisateurs (userId, movieId, rating)
```

## Algorithme

**Filtrage collaboratif item-item (Sarwar et al., 2001)**

1. **Matrice U×I** — pivot des notes utilisateur-film
2. **Centrage** — soustraction de la moyenne par utilisateur
3. **Similarité cosinus** entre colonnes (items)
4. **Prédiction** :

```
pred(u, i) = mean(u) + Σ sim(i,j)·(r(u,j) - mean(u)) / Σ|sim(i,j)|
```

## Pages de l'interface

| Page | Description |
|------|-------------|
| 🏠 Accueil | Stats dataset, distribution des notes, top films |
| 🔮 Prédiction | Note prédite pour un (user, film) + voisins utilisés |
| 🎯 Top-N | Films recommandés pour un utilisateur (non vus) |
| 🔗 Similarité | Films similaires + heatmap de la matrice de similarité |

## Paramètres (sidebar)

- **k voisins** : nombre de films similaires utilisés pour la prédiction (5–50)
- **Top-N** : nombre de recommandations à afficher (5–20)
