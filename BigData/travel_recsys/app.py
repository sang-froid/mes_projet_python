"""
WanderMatch — Système de Recommandation de Voyages
Interface professionnelle : images, vidéos, design ciel & mer
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from urllib.parse import quote
from recommender import TravelRecommender

# ─────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WanderMatch · Recommandation Voyage",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# STYLES — Palette ciel & mer
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── Background dégradé ciel ── */
.stApp {
    background: linear-gradient(160deg, #e8f4fd 0%, #d0e9f8 30%, #f0f8ff 70%, #e4f2fb 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a5c8a 0%, #1e3d6e 100%) !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] * { color: #d0e8f8 !important; }
section[data-testid="stSidebar"] .stMarkdown h3 { color: #fff !important; }
section[data-testid="stSidebar"] .stSlider > div > div { color: #d0e8f8 !important; }

/* ── Headings ── */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; }

/* ── Cards glass ── */
.glass-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.85);
    border-radius: 20px;
    padding: 22px 24px;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(30,90,150,0.08);
}

/* ── Destination card ── */
.dest-card {
    background: rgba(255,255,255,0.80);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 2px 16px rgba(30,90,150,0.10);
    transition: transform .18s, box-shadow .18s;
    margin-bottom: 14px;
    cursor: pointer;
}
.dest-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(30,90,150,0.18);
}
.dest-img {
    width: 100%; height: 180px;
    object-fit: cover; display: block;
    background: #c0d8f0;
}
.dest-body { padding: 14px 16px 16px; }
.dest-name {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem; font-weight: 700;
    color: #0f3a6e; margin: 0 0 2px;
}
.dest-region { font-size: .78rem; color: #5a85b0; margin-bottom: 6px; }
.dest-tagline { font-size: .82rem; color: #3a6090; line-height: 1.4; }

/* ── Reco card ── */
.reco-card {
    background: rgba(255,255,255,0.85);
    border: 1px solid rgba(255,255,255,0.95);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(30,90,150,0.12);
    margin-bottom: 18px;
    transition: transform .18s, box-shadow .18s;
}
.reco-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 36px rgba(30,90,150,0.20);
}
.reco-img { width: 100%; height: 220px; object-fit: cover; display: block; background: #c0d8f0; }
.reco-body { padding: 16px 18px 18px; }
.reco-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem; font-weight: 800;
    color: #0a2e58; margin: 0 0 3px;
}
.reco-region { font-size: .8rem; color: #4a7aaa; margin-bottom: 8px; }
.reco-score-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.reco-score {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem; font-weight: 800;
    color: #1a6bb5;
}
.reco-stars { color: #f0a820; font-size: 1rem; }
.reco-tagline { font-size: .84rem; color: #3a6090; margin-bottom: 10px; line-height: 1.4; }

/* ── Explanation pill ── */
.expl-pill {
    background: linear-gradient(90deg, #e8f3fc, #f0f8ff);
    border: 1px solid #b8d8f0;
    border-radius: 12px;
    padding: 8px 12px;
    font-size: .8rem;
    color: #2a5a8a;
    margin-bottom: 8px;
    line-height: 1.4;
}
.expl-social {
    background: linear-gradient(90deg, #e8f5ee, #f0fff5);
    border: 1px solid #a8d8b8;
    border-radius: 12px;
    padding: 8px 12px;
    font-size: .8rem;
    color: #1a5a3a;
    margin-bottom: 10px;
}

/* ── Buttons ── */
.btn-watch {
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg, #1a6bb5, #1450a0);
    color: #fff !important; border-radius: 10px;
    padding: 8px 16px; font-size: .82rem; font-weight: 600;
    font-family: 'Syne', sans-serif;
    text-decoration: none !important;
    transition: all .15s; margin-right: 8px; margin-top: 2px;
}
.btn-watch:hover { background: linear-gradient(135deg, #1450a0, #0f3a7a); color: #fff !important; }

.btn-yt {
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg, #c4180a, #a01008);
    color: #fff !important; border-radius: 10px;
    padding: 8px 16px; font-size: .82rem; font-weight: 600;
    font-family: 'Syne', sans-serif;
    text-decoration: none !important;
    transition: all .15s; margin-top: 2px;
}
.btn-yt:hover { background: linear-gradient(135deg, #a01008, #7a0806); color: #fff !important; }

/* ── Tags ── */
.tag {
    display: inline-block;
    background: rgba(26,107,181,0.10);
    border: 1px solid rgba(26,107,181,0.20);
    border-radius: 999px; padding: 3px 10px;
    font-size: .72rem; color: #1a5a9a;
    margin: 2px 2px;
}

/* ── Continent badge ── */
.cont-badge {
    display: inline-block;
    background: linear-gradient(90deg, #1a6bb5, #1a90d0);
    color: #fff; border-radius: 999px;
    padding: 3px 12px; font-size: .72rem; font-weight: 600;
    letter-spacing: .04em;
}

/* ── Seen pill ── */
.seen-pill {
    background: rgba(255,255,255,0.8);
    border: 1px solid rgba(26,107,181,0.25);
    border-radius: 14px; padding: 10px 14px;
    margin-bottom: 10px;
    display: flex; align-items: center; gap: 10px;
}
.seen-dest-name { font-weight: 600; color: #0f3a6e; font-size: .88rem; flex: 1; }

/* ── Metric box ── */
.met-box {
    background: rgba(255,255,255,0.7);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 14px; padding: 14px 16px; text-align: center;
    box-shadow: 0 2px 10px rgba(30,90,150,0.07);
}
.met-val {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem; font-weight: 800; color: #1a6bb5; line-height: 1;
}
.met-lbl { font-size: .72rem; color: #5a85b0; text-transform: uppercase; letter-spacing: .07em; margin-top: 4px; }

/* ── Search ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.85) !important;
    border: 1.5px solid rgba(26,107,181,0.25) !important;
    border-radius: 12px !important; color: #0f3a6e !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.85) !important;
    border: 1.5px solid rgba(26,107,181,0.25) !important;
    border-radius: 12px !important; color: #0f3a6e !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; color: #4a7aaa !important;
}
.stTabs [aria-selected="true"] { color: #1a6bb5 !important; border-bottom-color: #1a6bb5 !important; }

/* ── Streamlit button ── */
.stButton > button {
    background: linear-gradient(135deg, #1a6bb5, #1450a0) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    padding: .5rem 1.4rem !important;
    box-shadow: 0 4px 14px rgba(26,107,181,0.25) !important;
    transition: all .15s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1450a0, #0f3a7a) !important;
    box-shadow: 0 6px 20px rgba(26,107,181,0.35) !important;
}

/* ── Logo ── */
.logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem; font-weight: 800;
    color: #fff; letter-spacing: -.02em;
}
.logo-dot { color: #7dd3fc; }

/* ── Page hero ── */
.hero {
    background: linear-gradient(135deg, #1a6bb5 0%, #1a90d0 50%, #0ea5e9 100%);
    border-radius: 20px; padding: 32px 36px; margin-bottom: 28px;
    position: relative; overflow: hidden;
}
.hero::before {
    content: '✈️';
    position: absolute; right: 36px; top: 50%;
    transform: translateY(-50%);
    font-size: 5rem; opacity: .15;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem; font-weight: 800;
    color: #fff; margin: 0 0 6px; line-height: 1.1;
}
.hero-sub { font-size: .95rem; color: rgba(255,255,255,.8); margin: 0; }

/* ── Select slider ── */
.stSelectSlider > div { color: #0f3a6e !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# DATA & MODEL
# ─────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data
def load_data():
    ratings = pd.read_csv(DATA_DIR / "ratings.csv")
    dests   = pd.read_csv(DATA_DIR / "destinations.csv")
    return ratings, dests

@st.cache_resource
def load_model():
    ratings, dests = load_data()
    m = TravelRecommender(k_neighbors=15)
    m.fit(ratings, dests)
    return m

def unsplash_url(query: str, w=600, h=400) -> str:
    q = quote(query)
    return f"https://source.unsplash.com/{w}x{h}/?{q}"

def justwatch_url(name: str) -> str:
    return f"https://www.google.com/search?q={quote(name + ' voyage que voir faire')}+site:tripadvisor.fr+OR+site:lonelyplanet.fr"

def yt_url(name: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote(name + ' travel vlog 4K')}"

def stars(r: float) -> str:
    full = int(r); half = 1 if (r % 1) >= 0.5 else 0; empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty

def tag_html(tags_str: str) -> str:
    return " ".join(f'<span class="tag">{t.strip()}</span>' for t in tags_str.split("|"))

ratings_df, dests_df = load_data()
model = load_model()
stats = model.get_global_stats()

DEST_BY_ID  = dests_df.set_index("destId").to_dict("index")
ALL_IDS     = dests_df["destId"].tolist()

if "seen_ratings"    not in st.session_state: st.session_state.seen_ratings    = {}
if "recommendations" not in st.session_state: st.session_state.recommendations = []


# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="logo">✈️ Wander<span class="logo-dot">Match</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.72rem;color:#7ab8e0;margin-bottom:24px;">Recommandation de voyages · TP1</div>', unsafe_allow_html=True)

    st.markdown("### 🗺️ Destinations préférées")
    seen = st.session_state.seen_ratings
    if seen:
        avg_my = np.mean(list(seen.values()))
        st.markdown(f'<div style="color:#7dd3fc;font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;">{avg_my:.1f} ★</div><div style="color:#7ab8e0;font-size:.75rem;margin-bottom:12px;">{len(seen)} destination{"s" if len(seen)!=1 else ""} notée{"s" if len(seen)!=1 else ""}</div>', unsafe_allow_html=True)
        for did, r in seen.items():
            info = DEST_BY_ID.get(did, {})
            st.markdown(f'<div style="font-size:.82rem;color:#b0d8f4;padding:4px 0;border-bottom:1px solid rgba(255,255,255,.1);">📍 <b>{info.get("name","")}</b> · {r}★</div>', unsafe_allow_html=True)
        if st.button("🗑️ Réinitialiser"):
            st.session_state.seen_ratings = {}
            st.session_state.recommendations = []
            st.rerun()
    else:
        st.markdown('<div style="color:#7ab8e0;font-size:.82rem;">Ajoute des destinations depuis le catalogue</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Base de données")
    st.markdown(f'<div style="color:#b0d8f4;font-size:.85rem;">👥 {stats["n_users"]} voyageurs · 🌍 {stats["n_destinations"]} destinations · ⭐ {stats["n_ratings"]:,} avis</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<span style="font-size:.68rem;color:#4a7aaa;">Filtrage collaboratif item-item · Similarité cosinus</span>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🌍 Explorer les destinations", "✨ Mes recommandations", "🔗 Destinations similaires"])


# ═════════════════════════════════════════════════════════
# TAB 1 — CATALOGUE
# ═════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="hero">
      <div class="hero-title">Où voulez-vous aller ?</div>
      <div class="hero-sub">Notez les destinations que vous avez visitées · Notre IA découvrira vos prochains coups de cœur</div>
    </div>""", unsafe_allow_html=True)

    # Filtres
    col_s, col_c, col_t = st.columns([2, 1.5, 1.5])
    with col_s:
        search = st.text_input("", placeholder="🔍  Rechercher une destination…", label_visibility="collapsed")
    with col_c:
        continents = ["Tous les continents"] + sorted(dests_df["continent"].unique())
        cont_filter = st.selectbox("Continent", continents, label_visibility="collapsed")
    with col_t:
        tag_list = sorted({t for tags in dests_df["tags"] for t in tags.split("|")})
        tag_filter = st.selectbox("Thème", ["Tous les thèmes"] + tag_list, label_visibility="collapsed")

    # Filtrage
    filtered = dests_df.copy()
    if search:
        filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]
    if cont_filter != "Tous les continents":
        filtered = filtered[filtered["continent"] == cont_filter]
    if tag_filter != "Tous les thèmes":
        filtered = filtered[filtered["tags"].str.contains(tag_filter, na=False)]

    st.markdown(f'<div style="color:#4a7aaa;font-size:.82rem;margin-bottom:16px;">{len(filtered)} destination{"s" if len(filtered)!=1 else ""} trouvée{"s" if len(filtered)!=1 else ""}</div>', unsafe_allow_html=True)

    # Grille 3 colonnes
    cols_per_row = 3
    rows = [filtered.iloc[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]

    for row_df in rows:
        cols = st.columns(cols_per_row)
        for col, (_, dest) in zip(cols, row_df.iterrows()):
            did = int(dest["destId"])
            info = DEST_BY_ID[did]
            already = did in st.session_state.seen_ratings
            with col:
                img_url = unsplash_url(dest["unsplash_query"], 600, 400)
                st.markdown(f"""
                <div class="dest-card">
                  <img class="dest-img" src="{img_url}" alt="{dest['name']}" loading="lazy"/>
                  <div class="dest-body">
                    <div class="dest-name">{dest['name']}</div>
                    <div class="dest-region">📍 {dest['region']}</div>
                    <div style="margin-bottom:6px;">{tag_html(dest['tags'])}</div>
                    <div class="dest-tagline">{dest['tagline']}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

                btn_col, link_col = st.columns([1, 1])
                with btn_col:
                    if already:
                        st.success(f"✓ {st.session_state.seen_ratings[did]}★")
                    else:
                        if st.button("➕ J'y suis allé", key=f"add_{did}"):
                            st.session_state.seen_ratings[did] = 4.0
                            st.rerun()
                with link_col:
                    st.markdown(f'<a href="{yt_url(dest["name"])}" target="_blank" class="btn-yt">▶ Vidéo</a>', unsafe_allow_html=True)

    # ── Section notation ────────────────────────────────
    if st.session_state.seen_ratings:
        st.markdown("---")
        st.markdown("### ✍️ Ajuste tes notes")
        to_remove = []
        ncols = min(3, len(st.session_state.seen_ratings))
        cols = st.columns(ncols)
        for i, (did, rating) in enumerate(list(st.session_state.seen_ratings.items())):
            info = DEST_BY_ID.get(did, {})
            with cols[i % ncols]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,.7);border-radius:14px;padding:12px 14px;margin-bottom:8px;">
                  <div style="font-weight:700;color:#0f3a6e;font-size:.88rem;">📍 {info.get('name','')}</div>
                  <div style="font-size:.72rem;color:#4a7aaa;margin-bottom:8px;">{info.get('region','')}</div>
                </div>""", unsafe_allow_html=True)
                new_r = st.select_slider(
                    "Note", options=[1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0],
                    value=rating, format_func=lambda x: f"{x} ★",
                    key=f"rate_{did}", label_visibility="collapsed"
                )
                st.session_state.seen_ratings[did] = new_r
                if st.button("✕ Retirer", key=f"rm_{did}"):
                    to_remove.append(did)

        for did in to_remove:
            del st.session_state.seen_ratings[did]
        if to_remove:
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if len(st.session_state.seen_ratings) >= 2:
            if st.button("✨ Découvrir mes recommandations →", use_container_width=True):
                with st.spinner("Notre IA analyse tes goûts…"):
                    recs = model.predict_for_profile(st.session_state.seen_ratings, n=6)
                    # Merge destination info
                    for r in recs:
                        info = DEST_BY_ID.get(r["destId"], {})
                        r.update({
                            "name": info.get("name",""),
                            "region": info.get("region",""),
                            "tagline": info.get("tagline",""),
                            "tags": info.get("tags",""),
                            "unsplash_query": info.get("unsplash_query",""),
                        })
                    st.session_state.recommendations = recs
                st.success(f"✅ {len(recs)} recommandations générées ! Consulte l'onglet ✨")
        else:
            st.info("Ajoute au moins 2 destinations pour obtenir des recommandations.")


# ═════════════════════════════════════════════════════════
# TAB 2 — RECOMMANDATIONS
# ═════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="hero" style="background:linear-gradient(135deg,#0f766e 0%,#0ea5e9 100%);">
      <div class="hero-title">Vos prochaines aventures</div>
      <div class="hero-sub">Sélectionnées selon vos voyages passés · Avec liens pour planifier</div>
    </div>""", unsafe_allow_html=True)

    recs = st.session_state.recommendations

    if not recs:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:60px 30px;">
          <div style="font-size:3.5rem;margin-bottom:16px;">🧳</div>
          <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:#0f3a6e;margin-bottom:8px;">Aucune recommandation pour l'instant</div>
          <div style="color:#4a7aaa;">Note au moins 2 destinations dans <b>Explorer</b> puis clique sur<br><b>Découvrir mes recommandations</b></div>
        </div>""", unsafe_allow_html=True)
    else:
        avg_pred = np.mean([r["predicted_rating"] for r in recs])
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="met-box"><div class="met-val">{len(recs)}</div><div class="met-lbl">Destinations suggérées</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="met-box"><div class="met-val">{avg_pred:.1f}★</div><div class="met-lbl">Score moyen prédit</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="met-box"><div class="met-val">{len(st.session_state.seen_ratings)}</div><div class="met-lbl">Destinations notées</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2 colonnes de reco cards
        col_a, col_b = st.columns(2)
        for i, rec in enumerate(recs):
            target_col = col_a if i % 2 == 0 else col_b
            with target_col:
                img = unsplash_url(rec.get("unsplash_query", rec["name"]), 800, 500)
                score = rec["predicted_rating"]
                because = rec.get("because_of", [])
                social  = rec.get("social_explanation", "")

                st.markdown(f"""
                <div class="reco-card">
                  <img class="reco-img" src="{img}" alt="{rec['name']}" loading="lazy"/>
                  <div class="reco-body">
                    <div style="margin-bottom:6px;"><span class="cont-badge">#{i+1} Recommandation</span></div>
                    <div class="reco-title">{rec['name']}</div>
                    <div class="reco-region">📍 {rec.get('region','')}</div>
                    <div class="reco-score-row">
                      <span class="reco-score">{score}</span>
                      <span class="reco-stars">{stars(score)}</span>
                    </div>
                    <div class="reco-tagline">{rec.get('tagline','')}</div>
                    {tag_html(rec.get('tags',''))}
                </div>""", unsafe_allow_html=True)

                # Explications
                if because:
                    names = " et ".join(f"<b>{b['name']}</b>" for b in because[:2])
                    st.markdown(f'<div class="expl-pill">💡 Recommandé car similaire à {names} que vous avez aimés</div>', unsafe_allow_html=True)
                if social:
                    st.markdown(f'<div class="expl-social">👥 {social}</div>', unsafe_allow_html=True)

                # Boutons
                q = rec["name"]
                st.markdown(f"""
                <a href="{justwatch_url(q)}" target="_blank" class="btn-watch">🌐 Planifier</a>
                <a href="{yt_url(q)}" target="_blank" class="btn-yt">▶ Voir vidéos</a>
                """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)  # close reco-card
                st.markdown("<br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════
# TAB 3 — SIMILARITÉ
# ═════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="hero" style="background:linear-gradient(135deg,#4f46e5 0%,#0ea5e9 100%);">
      <div class="hero-title">Destinations similaires</div>
      <div class="hero-sub">Découvrez quelles destinations attirent les mêmes profils de voyageurs</div>
    </div>""", unsafe_allow_html=True)

    ref_id = st.selectbox(
        "Choisir une destination de référence",
        ALL_IDS,
        format_func=lambda x: f"{'📍'} {DEST_BY_ID[x]['name']}  ·  {DEST_BY_ID[x]['region']}",
    )

    ref_info = DEST_BY_ID[ref_id]

    col_ref, col_sim = st.columns([1, 2])
    with col_ref:
        img_ref = unsplash_url(ref_info["unsplash_query"], 600, 800)
        st.markdown(f"""
        <div class="reco-card">
          <img class="reco-img" src="{img_ref}" alt="{ref_info['name']}" style="height:260px;" loading="lazy"/>
          <div class="reco-body">
            <div class="reco-title">{ref_info['name']}</div>
            <div class="reco-region">📍 {ref_info['region']}</div>
            <div style="margin-bottom:8px;">{tag_html(ref_info['tags'])}</div>
            <div style="font-size:.84rem;color:#3a6090;">{ref_info['tagline']}</div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f'<a href="{yt_url(ref_info["name"])}" target="_blank" class="btn-yt" style="display:block;text-align:center;margin-top:-8px;">▶ Voir des vidéos de {ref_info["name"]}</a>', unsafe_allow_html=True)

    with col_sim:
        similars = model.get_similar_destinations(ref_id, n=5)
        st.markdown(f'<div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#0f3a6e;margin-bottom:14px;">Les 5 destinations les plus proches de {ref_info["name"]}</div>', unsafe_allow_html=True)

        for s in similars:
            sinfo = DEST_BY_ID.get(s["destId"], {})
            sim_pct = int(s["similarity"] * 100)
            img_sm = unsplash_url(sinfo.get("unsplash_query", sinfo.get("name","")), 200, 150)
            st.markdown(f"""
            <div style="background:rgba(255,255,255,.8);border:1px solid rgba(255,255,255,.95);border-radius:16px;padding:12px 16px;margin-bottom:10px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 10px rgba(30,90,150,.08);">
              <img src="{img_sm}" style="width:80px;height:60px;object-fit:cover;border-radius:10px;flex-shrink:0;" loading="lazy"/>
              <div style="flex:1;">
                <div style="font-family:Syne,sans-serif;font-weight:700;color:#0a2e58;font-size:.95rem;">{sinfo.get('name','')}</div>
                <div style="font-size:.75rem;color:#4a7aaa;margin-bottom:4px;">📍 {sinfo.get('region','')}</div>
                <div style="background:#e0eff8;border-radius:6px;height:6px;overflow:hidden;">
                  <div style="background:linear-gradient(90deg,#1a6bb5,#0ea5e9);height:100%;width:{sim_pct}%;border-radius:6px;"></div>
                </div>
                <div style="font-size:.72rem;color:#1a6bb5;margin-top:3px;">Similarité : {s['similarity']:.2f}</div>
              </div>
              <div>
                <a href="{yt_url(sinfo.get('name',''))}" target="_blank" class="btn-yt" style="padding:5px 10px;font-size:.72rem;">▶</a>
              </div>
            </div>""", unsafe_allow_html=True)
