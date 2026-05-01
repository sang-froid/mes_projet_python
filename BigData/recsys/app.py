"""
CineMatch — Système de Recommandation Collaboratif (Item-Item)
TP1 — Filtrage Collaboratif avec MovieLens
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

from recommender import ItemItemRecommender

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch · RecSys",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# STYLE
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: #0a0a0f;
    color: #e8e4dc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid #1e1e2e;
}
section[data-testid="stSidebar"] * { color: #c8c4bc !important; }

/* Headings */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* Cards */
.card {
    background: #12121c;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 16px;
}

.card-accent {
    border-color: #e05c2a;
    box-shadow: 0 0 24px rgba(224, 92, 42, 0.12);
}

/* Metric custom */
.metric-box {
    background: #16161f;
    border: 1px solid #272737;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
}
.metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: #e05c2a;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.78rem;
    color: #7a7a8c;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}

/* Tag genre */
.genre-tag {
    display: inline-block;
    background: #1e1e30;
    border: 1px solid #2e2e48;
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 0.75rem;
    color: #9090b0;
    margin: 2px 2px;
}

/* Star rating */
.stars { color: #e05c2a; font-size: 1.2rem; }

/* Page header */
.page-header {
    padding: 12px 0 28px 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 32px;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: #f0ece4;
    margin: 0;
}
.page-sub {
    color: #6a6a7c;
    font-size: 0.88rem;
    margin-top: 4px;
}

/* Prediction big */
.pred-score {
    font-family: 'Syne', sans-serif;
    font-size: 4rem;
    font-weight: 800;
    color: #e05c2a;
    line-height: 1;
}

/* Table override */
.dataframe { background: #12121c !important; }

/* Selectbox, sliders */
.stSelectbox > div, .stSlider > div { color: #e8e4dc !important; }

/* Plotly transparent bg */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }

/* Neighbor row */
.neighbor-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #1a1a28;
}
.neighbor-rank {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    color: #e05c2a;
    width: 28px;
    font-weight: 700;
}
.neighbor-title { flex: 1; font-size: 0.88rem; color: #d0cccc; }
.neighbor-sim {
    font-size: 0.82rem;
    color: #9090a8;
    width: 60px;
    text-align: right;
}
.neighbor-rating {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #e05c2a;
    width: 36px;
    text-align: right;
}

/* Logo banner */
.logo-banner {
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 800;
    color: #f0ece4;
    letter-spacing: -0.02em;
}
.logo-accent { color: #e05c2a; }

.stButton>button {
    background: #e05c2a !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.4rem !important;
}
.stButton>button:hover {
    background: #c44d20 !important;
}

hr { border-color: #1e1e2e !important; }

.info-pill {
    background: #1a1a2e;
    border: 1px solid #2a2a3e;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.8rem;
    color: #8080a0;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA & MODEL LOADING (cached)
# ─────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    ratings = pd.read_csv(DATA_DIR / "ratings.csv")
    movies = pd.read_csv(DATA_DIR / "movies.csv")
    return ratings, movies

@st.cache_resource
def load_model(k):
    ratings, movies = load_data()
    model = ItemItemRecommender(k_neighbors=k)
    model.fit(ratings, movies)
    return model

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def stars(rating: float) -> str:
    full = int(rating // 1)
    half = 1 if (rating % 1) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "½" * half + "☆" * empty

def genre_tags(genres_str: str) -> str:
    tags = genres_str.split("|") if genres_str else []
    return " ".join([f'<span class="genre-tag">{g}</span>' for g in tags])

def rating_bar(val: float, max_val: float = 5.0) -> str:
    pct = val / max_val * 100
    return f"""
    <div style="background:#1a1a28;border-radius:4px;height:6px;overflow:hidden;">
      <div style="background:#e05c2a;height:100%;width:{pct:.0f}%;border-radius:4px;"></div>
    </div>"""

def plotly_dark():
    return dict(
        plot_bgcolor="#0d0d16",
        paper_bgcolor="#12121c",
        font=dict(color="#c8c4bc", family="DM Sans"),
        xaxis=dict(gridcolor="#1e1e2e", linecolor="#1e1e2e"),
        yaxis=dict(gridcolor="#1e1e2e", linecolor="#1e1e2e"),
        margin=dict(l=16, r=16, t=32, b=16),
    )

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo-banner">🎬 Cine<span class="logo-accent">Match</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#4a4a5c;font-size:0.75rem;margin-bottom:24px;">Item-Item Collaborative Filtering</div>', unsafe_allow_html=True)

    st.markdown("### ⚙️ Paramètres du modèle")
    k_neighbors = st.slider("Voisins k (top-k items similaires)", min_value=5, max_value=50, value=20, step=5)
    n_reco = st.slider("Top-N recommandations", min_value=5, max_value=20, value=10, step=1)

    st.markdown("---")
    st.markdown("### 🔍 Navigation")
    page = st.radio(
        "Page",
        ["🏠 Accueil", "🔮 Prédiction de note", "🎯 Top-N Recommandations", "🔗 Similarité entre films"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    ratings_df, movies_df = load_data()
    model = load_model(k_neighbors)
    sparsity = model.get_sparsity()

    st.markdown("### 📊 Dataset")
    col1, col2 = st.columns(2)
    col1.metric("Users", ratings_df["userId"].nunique())
    col2.metric("Films", movies_df.shape[0])
    col1.metric("Notes", len(ratings_df))
    col2.metric("Sparsité", f"{sparsity*100:.1f}%")

    st.markdown('<span class="info-pill">MovieLens · Cosine Similarity</span>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE : ACCUEIL
# ─────────────────────────────────────────────
if page == "🏠 Accueil":
    st.markdown("""
    <div class="page-header">
      <p class="page-title">Système de Recommandation<br>Item-Item Collaboratif</p>
      <p class="page-sub">TP1 · MovieLens · Cosine Similarity · Filtrage collaboratif</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{ratings_df["userId"].nunique()}</div><div class="metric-label">Utilisateurs</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{movies_df.shape[0]}</div><div class="metric-label">Films</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{len(ratings_df):,}</div><div class="metric-label">Notes</div></div>', unsafe_allow_html=True)
    with c4:
        avg = ratings_df["rating"].mean()
        st.markdown(f'<div class="metric-box"><div class="metric-val">{avg:.2f}</div><div class="metric-label">Note moyenne</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📐 Comment ça marche ?")
        st.markdown("""
Le **filtrage collaboratif item-item** (Sarwar et al., 2001) prédit la note
qu'un utilisateur donnerait à un film, en se basant sur la ressemblance entre films.

**Étapes :**
1. **Matrice utilisateur-item** — chaque cellule = note donnée
2. **Centrage** — soustraction de la moyenne de chaque utilisateur
3. **Similarité cosinus** entre toutes les paires de films
4. **Prédiction** via agrégation pondérée des k voisins les plus proches
""")
        st.latex(r"\hat{r}_{u,i} = \bar{r}_u + \frac{\sum_{j \in N_k(i)} \text{sim}(i,j)\cdot(r_{u,j} - \bar{r}_u)}{\sum_{j \in N_k(i)} |\text{sim}(i,j)|}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Distribution des notes")
        dist = ratings_df["rating"].value_counts().sort_index()
        fig = go.Figure(go.Bar(
            x=dist.index.astype(str),
            y=dist.values,
            marker_color="#e05c2a",
            marker_line_width=0,
        ))
        fig.update_layout(**plotly_dark(), height=220, showlegend=False)
        fig.update_xaxes(title="Note")
        fig.update_yaxes(title="Nombre")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 🏆 Films les mieux notés (≥ 10 avis)")
    film_stats = ratings_df.groupby("movieId").agg(
        mean_rating=("rating", "mean"),
        n_ratings=("rating", "count"),
    ).reset_index()
    film_stats = film_stats[film_stats["n_ratings"] >= 10].sort_values("mean_rating", ascending=False).head(10)
    film_stats = film_stats.merge(movies_df, on="movieId")

    for _, row in film_stats.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{row['title']}**")
            st.markdown(genre_tags(row['genres']), unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stars">{stars(row["mean_rating"])}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<span style="color:#e05c2a;font-weight:700;">{row["mean_rating"]:.2f}</span> / 5', unsafe_allow_html=True)
        st.markdown(rating_bar(row["mean_rating"]), unsafe_allow_html=True)
        st.markdown("<hr style='margin:6px 0;border-color:#1a1a28;'>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE : PRÉDICTION
# ─────────────────────────────────────────────
elif page == "🔮 Prédiction de note":
    st.markdown("""
    <div class="page-header">
      <p class="page-title">🔮 Prédiction de Note</p>
      <p class="page-sub">Estimation de la note qu'un utilisateur donnerait à un film non encore vu</p>
    </div>
    """, unsafe_allow_html=True)

    all_users = model.get_all_users()
    all_movies = model.get_all_movies()

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
        st.markdown("#### Sélection")
        user_id = st.selectbox("👤 Utilisateur", all_users, format_func=lambda x: f"Utilisateur #{x}")
        movie_options = all_movies["movieId"].tolist()
        movie_titles = all_movies.set_index("movieId")["title"].to_dict()
        movie_id = st.selectbox("🎬 Film", movie_options, format_func=lambda x: movie_titles.get(x, f"Film #{x}"))
        predict_btn = st.button("Prédire la note →")
        st.markdown('</div>', unsafe_allow_html=True)

        # Stats utilisateur
        stats = model.get_user_stats(user_id)
        if stats:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"#### 👤 Profil — Utilisateur #{user_id}")
            m1, m2, m3 = st.columns(3)
            m1.metric("Notes données", stats["n_ratings"])
            m2.metric("Moyenne", stats["mean_rating"])
            m3.metric("Max", stats["max_rating"])

            st.markdown("**Derniers films notés :**")
            top_rated = stats["rated_movies"].head(5)
            for mid, r in top_rated.items():
                t = movie_titles.get(mid, f"Film #{mid}")
                st.markdown(f'<div class="neighbor-row"><span class="neighbor-title">{t[:40]}</span><span class="neighbor-rating">{r:.1f} ★</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if predict_btn or "last_pred" in st.session_state:
            if predict_btn:
                result = model.predict_rating(user_id, movie_id)
                st.session_state["last_pred"] = (user_id, movie_id, result)
            else:
                user_id, movie_id, result = st.session_state["last_pred"]

            movie_info = all_movies[all_movies["movieId"] == movie_id].iloc[0]
            movie_stats = model.get_movie_stats(movie_id)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"#### 🎬 {movie_info['title']}")
            st.markdown(genre_tags(movie_info['genres']), unsafe_allow_html=True)
            st.markdown(f"<br><small style='color:#6a6a7c;'>Noté par {movie_stats.get('n_ratings',0)} utilisateurs · Moyenne globale {movie_stats.get('mean_rating',0):.2f}/5</small>", unsafe_allow_html=True)
            st.markdown("---")

            if "error" in result:
                st.error(result["error"])
            else:
                pred = result["prediction"]
                col_score, col_star = st.columns([1, 1])
                with col_score:
                    st.markdown(f'<div class="pred-score">{pred}</div><div style="color:#6a6a7c;font-size:0.85rem;margin-top:4px;">/ 5.0 prédit</div>', unsafe_allow_html=True)
                with col_star:
                    st.markdown(f'<div class="stars" style="font-size:1.8rem;margin-top:12px;">{stars(pred)}</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:#1a1a28;border-radius:8px;padding:12px 16px;margin-top:16px;font-size:0.84rem;color:#9090a8;">
                  Méthode : Item-Item CF · Voisins utilisés : <b style="color:#e05c2a;">{result['n_neighbors']}</b> · 
                  Moyenne utilisateur : <b style="color:#e05c2a;">{result['user_mean']}</b>
                </div>""", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            if "error" not in result and result["neighbors"]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"#### 🔗 {len(result['neighbors'])} films voisins utilisés")
                st.markdown('<div style="color:#6a6a7c;font-size:0.8rem;margin-bottom:12px;">Films similaires que l\'utilisateur a déjà notés</div>', unsafe_allow_html=True)

                for i, n in enumerate(result["neighbors"], 1):
                    sim_pct = int(n["similarity"] * 100)
                    st.markdown(f"""
                    <div class="neighbor-row">
                      <span class="neighbor-rank">#{i}</span>
                      <span class="neighbor-title">{n['title'][:42]}</span>
                      <span style="font-size:0.75rem;color:#5a5a7c;width:70px;text-align:center;">sim {n['similarity']:.3f}</span>
                      <span class="neighbor-rating">{n['user_rating']} ★</span>
                    </div>""", unsafe_allow_html=True)

                # Mini bar chart similarités
                nb_df = pd.DataFrame(result["neighbors"]).head(8)
                fig = go.Figure(go.Bar(
                    x=nb_df["similarity"],
                    y=[t[:28] + "…" if len(t) > 28 else t for t in nb_df["title"]],
                    orientation="h",
                    marker_color="#e05c2a",
                    marker_line_width=0,
                ))
                fig.update_layout(**plotly_dark(), height=260, showlegend=False)
                fig.update_xaxes(title="Similarité cosinus", range=[0, 1])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px 20px;">
              <div style="font-size:3rem;margin-bottom:12px;">🔮</div>
              <div style="color:#6a6a7c;">Sélectionne un utilisateur et un film,<br>puis clique sur <b style="color:#e05c2a;">Prédire la note</b></div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE : TOP-N RECOMMANDATIONS
# ─────────────────────────────────────────────
elif page == "🎯 Top-N Recommandations":
    st.markdown("""
    <div class="page-header">
      <p class="page-title">🎯 Top-N Recommandations</p>
      <p class="page-sub">Films suggérés pour un utilisateur, qu'il n'a pas encore vus</p>
    </div>
    """, unsafe_allow_html=True)

    all_users = model.get_all_users()
    all_movies = model.get_all_movies()
    movie_titles = all_movies.set_index("movieId")["title"].to_dict()

    col_ctrl, col_res = st.columns([1, 2])

    with col_ctrl:
        st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
        user_id = st.selectbox("👤 Utilisateur", all_users, format_func=lambda x: f"Utilisateur #{x}", key="topn_user")
        reco_btn = st.button(f"Générer Top-{n_reco} →")
        st.markdown('</div>', unsafe_allow_html=True)

        stats = model.get_user_stats(user_id)
        if stats:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"#### 👤 Utilisateur #{user_id}")
            m1, m2 = st.columns(2)
            m1.metric("Films notés", stats["n_ratings"])
            m2.metric("Moyenne", stats["mean_rating"])
            st.markdown("**Films préférés :**")
            for mid, r in stats["rated_movies"].head(4).items():
                t = movie_titles.get(mid, f"#{mid}")
                st.markdown(f'<div class="neighbor-row"><span class="neighbor-title">{t[:34]}</span><span class="neighbor-rating">{r:.1f} ★</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_res:
        if reco_btn or f"reco_{user_id}" in st.session_state:
            if reco_btn:
                recs = model.recommend_top_n(user_id, n=n_reco)
                st.session_state[f"reco_{user_id}"] = recs
            else:
                recs = st.session_state[f"reco_{user_id}"]

            if recs.empty:
                st.warning("Pas assez de données pour cet utilisateur.")
            else:
                # Bar chart
                fig = go.Figure(go.Bar(
                    x=recs["predicted_rating"],
                    y=[t[:35] + "…" if len(t) > 35 else t for t in recs["title"]],
                    orientation="h",
                    marker=dict(
                        color=recs["predicted_rating"],
                        colorscale=[[0, "#1e1e2e"], [1, "#e05c2a"]],
                        showscale=False,
                        line_width=0,
                    ),
                    text=[f"{r:.2f}" for r in recs["predicted_rating"]],
                    textposition="outside",
                    textfont=dict(color="#e05c2a", size=11),
                ))
                fig.update_layout(**plotly_dark(), height=max(300, n_reco * 36), showlegend=False)
                fig.update_xaxes(title="Note prédite", range=[0, 5.3])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                # Table détaillée
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"#### 📋 Détail des {len(recs)} recommandations")
                for i, row in recs.iterrows():
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"**{i+1}. {row['title']}**")
                        st.markdown(genre_tags(row['genres']), unsafe_allow_html=True)
                    with c2:
                        st.markdown(f'<div class="stars">{stars(row["predicted_rating"])}</div>', unsafe_allow_html=True)
                        st.markdown(rating_bar(row["predicted_rating"]), unsafe_allow_html=True)
                    with c3:
                        st.markdown(f'<span style="color:#e05c2a;font-family:Syne,sans-serif;font-weight:700;font-size:1.1rem;">{row["predicted_rating"]:.2f}</span>', unsafe_allow_html=True)
                        st.caption(f"{row['n_neighbors']} voisins")
                    if i < len(recs) - 1:
                        st.markdown("<hr style='margin:6px 0;border-color:#1a1a28;'>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px 20px;">
              <div style="font-size:3rem;margin-bottom:12px;">🎯</div>
              <div style="color:#6a6a7c;">Sélectionne un utilisateur et clique sur<br><b style="color:#e05c2a;">Générer les recommandations</b></div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE : SIMILARITÉ
# ─────────────────────────────────────────────
elif page == "🔗 Similarité entre films":
    st.markdown("""
    <div class="page-header">
      <p class="page-title">🔗 Similarité entre Films</p>
      <p class="page-sub">Matrice de similarité cosinus item-item et films les plus proches</p>
    </div>
    """, unsafe_allow_html=True)

    all_movies = model.get_all_movies()
    movie_titles = all_movies.set_index("movieId")["title"].to_dict()

    tab1, tab2 = st.tabs(["🔍 Films similaires", "🗺️ Heatmap de similarité"])

    with tab1:
        col_l, col_r = st.columns([1, 1.4])

        with col_l:
            st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
            movie_id = st.selectbox(
                "🎬 Film de référence",
                all_movies["movieId"].tolist(),
                format_func=lambda x: movie_titles.get(x, f"Film #{x}"),
                key="sim_movie"
            )
            n_sim = st.slider("Nombre de voisins", 5, 20, 10)
            st.markdown('</div>', unsafe_allow_html=True)

            movie_info = all_movies[all_movies["movieId"] == movie_id].iloc[0]
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"#### 🎬 {movie_info['title']}")
            st.markdown(genre_tags(movie_info['genres']), unsafe_allow_html=True)
            mstats = model.get_movie_stats(movie_id)
            st.markdown(f"<br><b>{mstats.get('n_ratings',0)}</b> notes · Moyenne <b style='color:#e05c2a;'>{mstats.get('mean_rating',0):.2f}/5</b> · σ = {mstats.get('std_rating',0):.2f}", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            similar = model.get_similar_items(movie_id, n=n_sim)
            if not similar.empty:
                # Bar chart
                fig = go.Figure(go.Bar(
                    x=similar["similarity"],
                    y=[t[:32] + "…" if len(t) > 32 else t for t in similar["title"]],
                    orientation="h",
                    marker=dict(
                        color=similar["similarity"],
                        colorscale=[[0, "#1e1e30"], [1, "#e05c2a"]],
                        showscale=True,
                        colorbar=dict(title="Similarité", tickfont=dict(color="#9090a8"), titlefont=dict(color="#9090a8")),
                        line_width=0,
                    ),
                    text=[f"{s:.3f}" for s in similar["similarity"]],
                    textposition="outside",
                    textfont=dict(color="#e05c2a", size=10),
                ))
                fig.update_layout(**plotly_dark(), height=max(320, n_sim * 36), showlegend=False)
                fig.update_xaxes(title="Similarité cosinus", range=[0, 1.1])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"#### Films les plus proches de *{movie_info['title']}*")
                for _, row in similar.iterrows():
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"**{row['title']}**")
                        st.markdown(genre_tags(row['genres']), unsafe_allow_html=True)
                    with c2:
                        st.markdown(rating_bar(row["similarity"]), unsafe_allow_html=True)
                    with c3:
                        st.markdown(f'<span style="color:#e05c2a;font-weight:700;">{row["similarity"]:.3f}</span>', unsafe_allow_html=True)
                    st.markdown("<hr style='margin:5px 0;border-color:#1a1a28;'>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Sélectionne des films pour visualiser leur matrice de similarité")

        top_movies = ratings_df = load_data()[0]
        top_ids = top_movies.groupby("movieId").size().nlargest(30).index.tolist()
        top_titles = [movie_titles.get(m, f"#{m}") for m in top_ids]

        selected_titles = st.multiselect(
            "Films à inclure (max 15)",
            options=top_titles,
            default=top_titles[:10],
            max_selections=15,
        )

        if len(selected_titles) >= 2:
            title_to_id = {v: k for k, v in movie_titles.items()}
            selected_ids = [title_to_id[t] for t in selected_titles if t in title_to_id]

            submat = model.get_similarity_submatrix(selected_ids)

            fig = go.Figure(go.Heatmap(
                z=submat.values,
                x=[t[:20] + "…" if len(t) > 20 else t for t in submat.columns],
                y=[t[:20] + "…" if len(t) > 20 else t for t in submat.index],
                colorscale=[[0, "#0a0a0f"], [0.5, "#2a1a0f"], [1, "#e05c2a"]],
                zmin=0, zmax=1,
                text=np.round(submat.values, 2),
                texttemplate="%{text}",
                textfont=dict(size=9, color="white"),
                hoverongaps=False,
                colorbar=dict(
                    title="Similarité",
                    tickfont=dict(color="#9090a8"),
                    titlefont=dict(color="#9090a8"),
                ),
            ))
            fig.update_layout(
                **plotly_dark(),
                height=500,
                xaxis=dict(tickangle=-40, tickfont=dict(size=10)),
                yaxis=dict(tickfont=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Sélectionne au moins 2 films.")
        st.markdown('</div>', unsafe_allow_html=True)
