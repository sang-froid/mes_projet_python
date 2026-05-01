"""
CineMatch — TP1 Filtrage Collaboratif Item-Item
Interface : profil utilisateur → recommandations expliquées + bouton Regarder
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from urllib.parse import quote
from recommender import ItemItemRecommender

# ─────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch · RecSys TP1",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #080810; color: #ddd8ce; }

section[data-testid="stSidebar"] {
    background: #0c0c18 !important;
    border-right: 1px solid #181828;
}
section[data-testid="stSidebar"] * { color: #aaa8b0 !important; }
h1,h2,h3,h4 { font-family:'Syne',sans-serif !important; letter-spacing:-.02em; }

.card {
    background:#10101e; border:1px solid #1c1c30;
    border-radius:14px; padding:22px 24px; margin-bottom:14px;
}
.card-hot { border-color:#d4501e; box-shadow:0 0 28px rgba(212,80,30,.10); }

.mbox { background:#14141f; border:1px solid #202030; border-radius:10px; padding:14px 16px; text-align:center; }
.mval { font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:#d4501e; line-height:1; }
.mlbl { font-size:.72rem; color:#60607a; text-transform:uppercase; letter-spacing:.08em; margin-top:4px; }

.gtag {
    display:inline-block; background:#18182c; border:1px solid #28283c;
    border-radius:999px; padding:2px 10px;
    font-size:.72rem; color:#8080a0; margin:2px 2px;
}

/* ── Watch button ───────────────────────────── */
.watch-btn {
    display:inline-flex; align-items:center; gap:6px;
    background:#d4501e; color:#fff !important;
    border-radius:8px; padding:6px 14px;
    font-family:'Syne',sans-serif; font-size:.8rem; font-weight:700;
    text-decoration:none !important;
    transition:background .15s;
    margin-top:6px;
}
.watch-btn:hover { background:#b84218; color:#fff !important; }

.watch-btn-sm {
    display:inline-flex; align-items:center; gap:5px;
    background:#1e1e10; border:1px solid #d4501e; color:#d4501e !important;
    border-radius:6px; padding:3px 10px;
    font-size:.75rem; font-weight:700; font-family:'Syne',sans-serif;
    text-decoration:none !important;
    transition:all .15s;
}
.watch-btn-sm:hover { background:#d4501e; color:#fff !important; }

/* ── Film chips ─────────────────────────────── */
.film-chip {
    background:#14141f; border:1px solid #202030; border-radius:10px;
    padding:10px 14px; margin-bottom:8px;
}
.chip-title { font-size:.85rem; color:#ccc8c4; }
.chip-genre { font-size:.7rem; color:#50507a; }

/* ── Reco card ──────────────────────────────── */
.reco-score {
    font-family:'Syne',sans-serif;
    font-size:2.2rem; font-weight:800;
    color:#d4501e; line-height:1;
}
.expl-box {
    background:#0e0e1c; border-left:3px solid #d4501e;
    border-radius:0 8px 8px 0; padding:10px 14px;
    margin-top:10px; font-size:.82rem; color:#9090a8; line-height:1.5;
}
.expl-label {
    font-size:.68rem; font-weight:700;
    text-transform:uppercase; letter-spacing:.1em;
    color:#d4501e; margin-bottom:3px;
}

.stars { color:#d4501e; }

.stButton>button {
    background:#d4501e !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-family:'Syne',sans-serif !important; font-weight:700 !important;
    padding:.45rem 1.4rem !important; transition:background .15s !important;
}
.stButton>button:hover { background:#b84218 !important; }

.stTabs [data-baseweb="tab"] {
    font-family:'Syne',sans-serif !important; font-weight:700 !important; color:#6a6a80 !important;
}
.stTabs [aria-selected="true"] { color:#d4501e !important; }

.logo { font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800; color:#f0ece4; }
.logo-dot { color:#d4501e; }

.ph { padding:8px 0 24px; border-bottom:1px solid #181828; margin-bottom:28px; }
.ph-title { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:#f0ece4; }
.ph-sub { font-size:.84rem; color:#50507a; margin-top:4px; }

hr { border-color:#181828 !important; }

.nb-row {
    display:flex; align-items:center; gap:10px;
    padding:8px 0; border-bottom:1px solid #181828; font-size:.82rem;
}
.nb-title { flex:1; color:#b0acb4; }
.nb-sim { width:56px; text-align:right; color:#606080; }
.nb-rat { width:36px; text-align:right; color:#d4501e; font-weight:700; font-family:'Syne',sans-serif; }

.pbar-wrap { background:#181828; border-radius:4px; height:5px; overflow:hidden; margin-top:4px; }
.pbar-fill { background:#d4501e; height:100%; border-radius:4px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# DONNÉES & MODÈLE
# ─────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    ratings = pd.read_csv(DATA_DIR / "ratings.csv")
    movies  = pd.read_csv(DATA_DIR / "movies.csv")
    return ratings, movies

@st.cache_resource
def load_model(k):
    ratings, movies = load_data()
    model = ItemItemRecommender(k_neighbors=k)
    model.fit(ratings, movies)
    return model

def stars(r: float) -> str:
    full  = int(r)
    half  = 1 if (r % 1) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "½" * half + "☆" * empty

def genre_tags(g: str) -> str:
    return " ".join(f'<span class="gtag">{t}</span>' for t in g.split("|")) if g else ""

def pbar(val, mx=5.0):
    pct = val / mx * 100
    return f'<div class="pbar-wrap"><div class="pbar-fill" style="width:{pct:.0f}%"></div></div>'

def plotly_dark():
    return dict(
        plot_bgcolor="#0c0c18", paper_bgcolor="#10101e",
        font=dict(color="#a0a0b8", family="DM Sans"),
        xaxis=dict(gridcolor="#181828", linecolor="#181828"),
        yaxis=dict(gridcolor="#181828", linecolor="#181828"),
        margin=dict(l=12, r=12, t=28, b=12),
    )

def watch_button(title: str, size: str = "normal") -> str:
    """Génère un lien JustWatch → si non trouvé, YouTube trailer."""
    q = quote(title)
    justwatch_url = f"https://www.justwatch.com/fr/recherche?q={q}"
    youtube_url   = f"https://www.youtube.com/results?search_query={q}+trailer+official"
    cls = "watch-btn" if size == "normal" else "watch-btn-sm"
    # Lien principal JustWatch + lien alternatif YouTube
    return (
        f'<a href="{justwatch_url}" target="_blank" class="{cls}">▶ Regarder</a>'
        f'&nbsp;<a href="{youtube_url}" target="_blank" class="watch-btn-sm">🎞 Trailer</a>'
    )

ratings_df, movies_df = load_data()
MOVIE_TITLES  = movies_df.set_index("movieId")["title"].to_dict()
MOVIE_GENRES  = movies_df.set_index("movieId")["genres"].to_dict()
ALL_MOVIE_IDS = movies_df["movieId"].tolist()

if "seen_ratings"    not in st.session_state: st.session_state.seen_ratings    = {}
if "recommendations" not in st.session_state: st.session_state.recommendations = []


# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo">🎬 Cine<span class="logo-dot">Match</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.72rem;color:#30305a;margin-bottom:20px;">Item-Item Collaborative Filtering · TP1</div>', unsafe_allow_html=True)

    st.markdown("### ⚙️ Paramètres")
    k_neighbors = st.slider("Voisins k", 5, 40, 20, 5)
    n_reco      = st.slider("Top-N recommandations", 5, 20, 8)

    model = load_model(k_neighbors)
    stats = model.get_global_stats()

    st.markdown("---")
    st.markdown("### 📊 Dataset")
    c1, c2 = st.columns(2)
    c1.metric("Users",   stats["n_users"])
    c2.metric("Films",   stats["n_movies"])
    c1.metric("Notes",   f"{stats['n_ratings']:,}")
    c2.metric("Sparsité",f"{stats['sparsity']*100:.1f}%")

    st.markdown("---")
    seen_count = len(st.session_state.seen_ratings)
    st.markdown(f"### 🎬 Mon profil · {seen_count} film{'s' if seen_count!=1 else ''}")
    if st.session_state.seen_ratings:
        avg_my = np.mean(list(st.session_state.seen_ratings.values()))
        st.markdown(f'<div style="color:#d4501e;font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;">{avg_my:.1f} ★</div><div style="color:#50507a;font-size:.75rem;">moyenne de mes notes</div>', unsafe_allow_html=True)
        if st.button("🗑️ Réinitialiser le profil"):
            st.session_state.seen_ratings    = {}
            st.session_state.recommendations = []
            st.rerun()

    st.markdown("---")
    st.markdown('<span style="font-size:.7rem;color:#303050;">150 films réels · MovieLens-style · Cosine Similarity</span>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎬 Mon Profil", "✨ Recommandations", "🔗 Similarité"])


# ═════════════════════════════════════════════════════════
# TAB 1 — PROFIL UTILISATEUR
# ═════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="ph">
      <div class="ph-title">🎬 Construis ton profil cinéma</div>
      <div class="ph-sub">Ajoute les films que tu as vus, donne ta note — le système apprend tes goûts</div>
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1.1, 1], gap="large")

    # ── Catalogue ───────────────────────────────────────
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 🔍 Catalogue")

        search = st.text_input("Rechercher…", placeholder="Inception, Dune, Parasite…", label_visibility="collapsed")
        all_genres = sorted({g for gs in MOVIE_GENRES.values() for g in gs.split("|")})
        genre_filter = st.selectbox("Genre", ["Tous les genres"] + all_genres, label_visibility="collapsed")

        filtered = movies_df.copy()
        if search:
            filtered = filtered[filtered["title"].str.contains(search, case=False, na=False)]
        if genre_filter != "Tous les genres":
            filtered = filtered[filtered["genres"].str.contains(genre_filter, na=False)]
        filtered = filtered[~filtered["movieId"].isin(st.session_state.seen_ratings.keys())]
        filtered = filtered.head(25)

        st.markdown(f'<div style="color:#50507a;font-size:.75rem;margin-bottom:10px;">{len(filtered)} résultats</div>', unsafe_allow_html=True)

        for _, row in filtered.iterrows():
            mid   = int(row["movieId"])
            title = row["title"]
            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                st.markdown(f"""
                <div class="film-chip">
                  <div class="chip-title">{title}</div>
                  <div class="chip-genre">{row['genres'].replace('|',' · ')}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                # Bouton regarder directement depuis le catalogue
                st.markdown(watch_button(title, "sm"), unsafe_allow_html=True)
            with c3:
                if st.button("➕", key=f"add_{mid}", help="Ajouter à mes films vus"):
                    st.session_state.seen_ratings[mid] = 3.5
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Films vus + notation ────────────────────────────
    with right:
        st.markdown('<div class="card card-hot">', unsafe_allow_html=True)
        st.markdown("#### ✅ Films vus — ma notation")

        if not st.session_state.seen_ratings:
            st.markdown("""
            <div style="text-align:center;padding:40px 10px;color:#404060;">
              <div style="font-size:2.5rem;margin-bottom:10px;">👈</div>
              <div>Ajoute des films depuis le catalogue<br>pour construire ton profil</div>
            </div>""", unsafe_allow_html=True)
        else:
            to_remove = []
            for mid, rating in list(st.session_state.seen_ratings.items()):
                title  = MOVIE_TITLES.get(mid, f"Film #{mid}")
                genres = MOVIE_GENRES.get(mid, "")

                st.markdown(f"""
                <div style="margin-bottom:2px;">
                  <div style="font-size:.85rem;color:#d0ccc8;font-weight:500;">{title}</div>
                  <div style="font-size:.68rem;color:#404060;">{genres.replace('|',' · ')}</div>
                </div>""", unsafe_allow_html=True)

                col_star, col_watch, col_rm = st.columns([4, 2, 1])
                with col_star:
                    new_r = st.select_slider(
                        "Note", options=[1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0],
                        value=rating, format_func=lambda x: f"{x} ★",
                        key=f"rate_{mid}", label_visibility="collapsed",
                    )
                    st.session_state.seen_ratings[mid] = new_r
                with col_watch:
                    st.markdown(watch_button(title, "sm"), unsafe_allow_html=True)
                with col_rm:
                    if st.button("✕", key=f"rm_{mid}"):
                        to_remove.append(mid)

                st.markdown("<hr style='margin:8px 0;border-color:#181828;'>", unsafe_allow_html=True)

            for mid in to_remove:
                del st.session_state.seen_ratings[mid]
            if to_remove:
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        if len(st.session_state.seen_ratings) >= 2:
            if st.button(f"✨ Générer mes {n_reco} recommandations →", use_container_width=True):
                with st.spinner("Calcul en cours…"):
                    recs = model.predict_for_user_profile(st.session_state.seen_ratings, n=n_reco)
                    st.session_state.recommendations = recs
                st.success(f"✅ {len(recs)} recommandations prêtes ! Consulte l'onglet ✨")
        elif st.session_state.seen_ratings:
            st.info("Ajoute au moins 2 films pour générer des recommandations.")


# ═════════════════════════════════════════════════════════
# TAB 2 — RECOMMANDATIONS
# ═════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="ph">
      <div class="ph-title">✨ Recommandations personnalisées</div>
      <div class="ph-sub">Films prédits selon tes goûts · Explication item-item + sociale · Liens pour regarder</div>
    </div>""", unsafe_allow_html=True)

    recs = st.session_state.recommendations

    if not recs:
        st.markdown("""
        <div class="card" style="text-align:center;padding:60px 20px;">
          <div style="font-size:3rem;margin-bottom:12px;">✨</div>
          <div style="color:#50507a;">Note au moins 2 films dans <b style="color:#d4501e;">Mon Profil</b>,<br>puis clique sur <b style="color:#d4501e;">Générer mes recommandations</b></div>
        </div>""", unsafe_allow_html=True)
    else:
        # Métriques
        avg_pred = np.mean([r["predicted_rating"] for r in recs])
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="mbox"><div class="mval">{len(recs)}</div><div class="mlbl">Recommandations</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="mbox"><div class="mval">{avg_pred:.2f}</div><div class="mlbl">Note prédite moy.</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="mbox"><div class="mval">{len(st.session_state.seen_ratings)}</div><div class="mlbl">Films dans mon profil</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Bar chart
        titles_short = [r["title"][:34] + "…" if len(r["title"]) > 34 else r["title"] for r in recs]
        preds = [r["predicted_rating"] for r in recs]
        fig = go.Figure(go.Bar(
            x=preds, y=titles_short, orientation="h",
            marker=dict(
                color=preds,
                colorscale=[[0,"#1a1a2e"],[1,"#d4501e"]],
                showscale=False, line_width=0,
            ),
            text=[f"{p:.2f} ★" for p in preds],
            textposition="outside",
            textfont=dict(color="#d4501e", size=11),
        ))
        fig.update_layout(**plotly_dark(), height=max(280, len(recs)*38), showlegend=False)
        fig.update_xaxes(title="Note prédite", range=[0,5.6])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### 📋 Détail & Explications")

        for i, rec in enumerate(recs):
            pred = rec["predicted_rating"]
            fire = "🔥" if pred >= 4.2 else ""

            with st.expander(f"#{i+1}  {rec['title']}  ·  {pred} ★  {fire}"):
                col_info, col_score = st.columns([3, 1])

                with col_info:
                    st.markdown(genre_tags(rec["genres"]), unsafe_allow_html=True)
                    st.markdown(f'<div style="color:#60607a;font-size:.78rem;margin-top:6px;">{rec["n_neighbors"]} films voisins utilisés</div>', unsafe_allow_html=True)
                    # ── Bouton Regarder bien visible ──────
                    st.markdown(f'<div style="margin-top:10px;">{watch_button(rec["title"])}</div>', unsafe_allow_html=True)

                with col_score:
                    st.markdown(f'<div class="reco-score">{pred}</div><div style="font-size:.75rem;color:#60607a;">/ 5.0 prédit</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stars" style="font-size:1.1rem;">{stars(pred)}</div>', unsafe_allow_html=True)

                # ── Explication Item-Item ─────────────────
                if rec.get("explanation_item"):
                    st.markdown(f"""
                    <div class="expl-box">
                      <div class="expl-label">🎬 Pourquoi ? — Similarité item-item</div>
                      {rec["explanation_item"]}
                    </div>""", unsafe_allow_html=True)

                    if rec.get("top_similar_seen"):
                        st.markdown('<div style="margin-top:10px;margin-bottom:4px;font-size:.75rem;color:#50507a;text-transform:uppercase;letter-spacing:.08em;">Films similaires que tu as notés</div>', unsafe_allow_html=True)
                        for nb in rec["top_similar_seen"]:
                            sentiment = "❤️" if nb["your_rating"] >= 4 else ("👍" if nb["your_rating"] >= 3 else "😐")
                            st.markdown(f"""
                            <div class="nb-row">
                              <span>{sentiment}</span>
                              <span class="nb-title">{nb['title']}</span>
                              <span class="nb-sim">sim {nb['similarity']:.3f}</span>
                              <span class="nb-rat">{nb['your_rating']} ★</span>
                            </div>""", unsafe_allow_html=True)
                            st.markdown(pbar(nb["similarity"], 1.0), unsafe_allow_html=True)

                # ── Explication Sociale ───────────────────
                if rec.get("explanation_user"):
                    st.markdown(f"""
                    <div class="expl-box" style="border-color:#3a3a10;margin-top:10px;">
                      <div class="expl-label" style="color:#a09010;">👥 Pourquoi ? — Utilisateurs similaires</div>
                      {rec["explanation_user"]}
                    </div>""", unsafe_allow_html=True)

                    if rec.get("similar_users_info"):
                        st.markdown('<div style="margin-top:10px;font-size:.75rem;color:#50507a;text-transform:uppercase;letter-spacing:.08em;">Utilisateurs similaires</div>', unsafe_allow_html=True)
                        for u in rec["similar_users_info"][:4]:
                            st.markdown(f"""
                            <div class="nb-row">
                              <span class="nb-title">User #{u['userId']} · {u['n_common']} films en commun</span>
                              <span class="nb-sim">sim {u['similarity']:.2f}</span>
                              <span class="nb-rat">{u['their_rating']} ★</span>
                            </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════
# TAB 3 — SIMILARITÉ
# ═════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="ph">
      <div class="ph-title">🔗 Similarité entre films</div>
      <div class="ph-sub">Matrice de similarité cosinus item-item — base du système de recommandation</div>
    </div>""", unsafe_allow_html=True)

    sub1, sub2 = st.tabs(["🔍 Films similaires", "🗺️ Heatmap"])

    with sub1:
        col_l, col_r = st.columns([1, 1.4])
        with col_l:
            st.markdown('<div class="card card-hot">', unsafe_allow_html=True)
            movie_id_sim = st.selectbox(
                "Film de référence", ALL_MOVIE_IDS,
                format_func=lambda x: MOVIE_TITLES.get(x, f"Film #{x}"),
            )
            n_sim = st.slider("Nombre de voisins", 5, 20, 10)
            st.markdown('</div>', unsafe_allow_html=True)

            mrow = movies_df[movies_df["movieId"] == movie_id_sim].iloc[0]
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"**{mrow['title']}**")
            st.markdown(genre_tags(mrow['genres']), unsafe_allow_html=True)
            rc = ratings_df[ratings_df["movieId"] == movie_id_sim]["rating"]
            if len(rc):
                st.markdown(f"<br><span style='color:#d4501e;font-weight:700;font-family:Syne,sans-serif;'>{rc.mean():.2f} ★</span> <span style='color:#50507a;font-size:.8rem;'>· {len(rc)} avis</span>", unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:10px;">{watch_button(mrow["title"])}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            sim_df = model.get_similar_items(movie_id_sim, n=n_sim)
            if not sim_df.empty:
                fig = go.Figure(go.Bar(
                    x=sim_df["similarity"],
                    y=[t[:30]+"…" if len(t)>30 else t for t in sim_df["title"]],
                    orientation="h",
                    marker=dict(
                        color=sim_df["similarity"],
                        colorscale=[[0,"#141428"],[1,"#d4501e"]],
                        showscale=True,
                        colorbar=dict(
                            title=dict(text="Sim.", font=dict(color="#8080a0")),
                            tickfont=dict(color="#8080a0"),
                        ),
                        line_width=0,
                    ),
                    text=[f"{s:.3f}" for s in sim_df["similarity"]],
                    textposition="outside",
                    textfont=dict(color="#d4501e", size=10),
                ))
                fig.update_layout(**plotly_dark(), height=max(320, n_sim*36), showlegend=False)
                fig.update_xaxes(title="Similarité cosinus", range=[0, 1.12])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                for _, row in sim_df.iterrows():
                    c1, c2, c3, c4 = st.columns([3, 2, 1, 2])
                    with c1:
                        st.markdown(f"**{row['title']}**")
                        st.markdown(genre_tags(row['genres']), unsafe_allow_html=True)
                    with c2:
                        st.markdown(pbar(row["similarity"], 1.0), unsafe_allow_html=True)
                    with c3:
                        st.markdown(f'<span style="color:#d4501e;font-family:Syne,sans-serif;font-weight:700;">{row["similarity"]:.3f}</span>', unsafe_allow_html=True)
                    with c4:
                        st.markdown(watch_button(row["title"], "sm"), unsafe_allow_html=True)
                    st.markdown("<hr style='margin:5px 0;border-color:#181828;'>", unsafe_allow_html=True)

    with sub2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Heatmap — sélectionne jusqu'à 15 films")

        top_ids    = ratings_df.groupby("movieId").size().nlargest(30).index.tolist()
        top_titles = [MOVIE_TITLES.get(m, f"#{m}") for m in top_ids]
        title_to_id = {MOVIE_TITLES.get(m): m for m in top_ids}

        selected = st.multiselect("Films", top_titles, default=top_titles[:10], max_selections=15, label_visibility="collapsed")

        if len(selected) >= 2:
            sel_ids = [title_to_id[t] for t in selected if t in title_to_id]
            submat  = model.get_similarity_submatrix(sel_ids)
            short   = [c[:20]+"…" if len(c)>20 else c for c in submat.columns]
            fig = go.Figure(go.Heatmap(
                z=submat.values, x=short, y=short,
                colorscale=[[0,"#080810"],[0.5,"#2a1a08"],[1,"#d4501e"]],
                zmin=0, zmax=1,
                text=np.round(submat.values, 2),
                texttemplate="%{text}",
                textfont=dict(size=9, color="white"),
                colorbar=dict(
                    title=dict(text="Sim.", font=dict(color="#8080a0")),
                    tickfont=dict(color="#8080a0"),
                ),
            ))
            _hl = plotly_dark()
            _hl['height'] = 500
            _hl['xaxis'] = dict(gridcolor='#181828', linecolor='#181828', tickangle=-38, tickfont=dict(size=9))
            _hl['yaxis'] = dict(gridcolor='#181828', linecolor='#181828', tickfont=dict(size=9))
            fig.update_layout(**_hl)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Sélectionne au moins 2 films.")
        st.markdown('</div>', unsafe_allow_html=True)
