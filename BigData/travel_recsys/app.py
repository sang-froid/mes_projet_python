"""
WanderMatch — Système de Recommandation de Destinations
Interface premium pour soutenance
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from urllib.parse import quote
import base64
from recommender import TravelRecommender

st.set_page_config(
    page_title="WanderMatch",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
# STYLES — Dark luxury travel theme
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ─ APP BACKGROUND ─────────────────────────────── */
.stApp {
    background: #0a0e1a;
    color: #e8e4dc;
}

/* ─ SIDEBAR ─────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0d1120 !important;
    border-right: 1px solid #1e2538 !important;
    width: 280px !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ─ HIDE DEFAULT STREAMLIT ELEMENTS ──────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ─ SIDEBAR CONTENT ──────────────────────────────── */
.sb-logo {
    padding: 28px 24px 20px;
    border-bottom: 1px solid #1e2538;
}
.sb-logo-text {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem; font-weight: 900;
    color: #fff; letter-spacing: -.02em;
}
.sb-logo-sub { font-size: .72rem; color: #5a6580; letter-spacing: .12em; text-transform: uppercase; margin-top: 2px; }

.sb-section { padding: 20px 24px 8px; font-size: .68rem; color: #3a4558; letter-spacing: .12em; text-transform: uppercase; }

.sb-profile-card {
    margin: 8px 12px 4px;
    background: #131826;
    border: 1px solid #1e2538;
    border-radius: 12px;
    padding: 14px 16px;
}
.sb-dest-item {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid #1e2538;
    font-size: .8rem; color: #8a95aa;
}
.sb-dest-item:last-child { border-bottom: none; }
.sb-dest-name { flex: 1; color: #c8c0b0; }
.sb-dest-stars { color: #d4a844; font-size: .75rem; }

.sb-stat {
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 0; font-size: .78rem; color: #6a7590;
    border-bottom: 1px solid #1a1f30;
}
.sb-stat-val { color: #d4a844; font-weight: 600; }

/* ─ MAIN CONTENT ─────────────────────────────────── */
.main-content {
    padding: 0 0 40px;
}

/* ─ HERO SECTION ──────────────────────────────────── */
.hero-section {
    position: relative;
    height: 420px;
    overflow: hidden;
    display: flex;
    align-items: flex-end;
    background: #0a0e1a;
}
.hero-bg {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    filter: brightness(.45);
}
.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, transparent 30%, #0a0e1a 100%);
}
.hero-content {
    position: relative;
    z-index: 2;
    padding: 0 48px 48px;
    width: 100%;
}
.hero-eyebrow {
    font-size: .72rem; font-weight: 600; letter-spacing: .18em;
    text-transform: uppercase; color: #d4a844;
    margin-bottom: 10px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem; font-weight: 900;
    color: #fff; line-height: 1.05;
    margin: 0 0 10px;
}
.hero-title span { color: #d4a844; }
.hero-sub {
    font-size: .95rem; color: rgba(255,255,255,.6);
    max-width: 500px; line-height: 1.6;
}

/* ─ SECTION HEADERS ──────────────────────────────── */
.section-header {
    display: flex; align-items: baseline; gap: 12px;
    padding: 32px 40px 16px;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem; font-weight: 700;
    color: #e8e4dc;
}
.section-count {
    font-size: .78rem; color: #4a5570;
    background: #131826; border-radius: 999px;
    padding: 3px 10px;
}

/* ─ DESTINATION CARD (catalogue) ─────────────────── */
.dest-card {
    background: #0f1422;
    border: 1px solid #1e2538;
    border-radius: 16px;
    overflow: hidden;
    transition: transform .2s, border-color .2s, box-shadow .2s;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.dest-card:hover {
    transform: translateY(-4px);
    border-color: #d4a844;
    box-shadow: 0 16px 48px rgba(0,0,0,.5);
}
/* FIX: image en cover avec hauteur fixe */
.dest-card-img-wrap {
    width: 100%;
    height: 160px;
    overflow: hidden;
    flex-shrink: 0;
    background: #131826;
}
.dest-card-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
    transition: transform .3s;
}
.dest-card:hover .dest-card-img {
    transform: scale(1.05);
}
.dest-card-body {
    padding: 14px 16px 16px;
    flex: 1;
    display: flex;
    flex-direction: column;
}
.dest-card-name {
    font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 700;
    color: #e8e4dc; margin: 0 0 2px;
}
.dest-card-region { font-size: .72rem; color: #5a6580; margin-bottom: 6px; }
.dest-card-tagline {
    font-size: .78rem;
    color: #8a95aa;
    line-height: 1.4;
    margin-bottom: 8px;
    flex: 1;
}
.dest-tag {
    display: inline-block;
    background: #131826; border: 1px solid #1e2538;
    border-radius: 999px; padding: 2px 8px;
    font-size: .65rem; color: #6a7590; margin: 1px 1px;
}
.dest-card-footer {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 10px; padding-top: 10px;
    border-top: 1px solid #1a1f30;
}
.dest-avg { font-size: .75rem; color: #d4a844; }

/* ─ BUTTONS ───────────────────────────────────────── */
.btn-yt {
    display: inline-flex; align-items: center; gap: 5px;
    background: transparent; border: 1px solid #1e2538;
    color: #6a7590 !important;
    border-radius: 8px; padding: 5px 10px;
    font-size: .75rem; font-weight: 500;
    text-decoration: none !important;
    transition: all .15s;
}
.btn-yt:hover { border-color: #c4180a; color: #c4180a !important; }

/* ─ RECO CARD ─────────────────────────────────────── */
.reco-card {
    background: #0f1422;
    border: 1px solid #1e2538;
    border-radius: 20px;
    overflow: hidden;
    transition: transform .2s, box-shadow .2s;
    margin-bottom: 20px;
}
.reco-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 24px 64px rgba(0,0,0,.6);
}
/* FIX: image reco en cover */
.reco-img-wrap {
    position: relative;
    width: 100%;
    height: 260px;
    overflow: hidden;
}
.reco-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
    background: #131826;
    transition: transform .4s;
}
.reco-card:hover .reco-img {
    transform: scale(1.04);
}
.reco-rank-badge {
    position: absolute; top: 14px; left: 14px;
    background: rgba(10,14,26,.75);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(212,168,68,.4);
    border-radius: 8px; padding: 4px 10px;
    font-size: .7rem; font-weight: 700;
    color: #d4a844; letter-spacing: .1em; text-transform: uppercase;
}
.reco-score-badge {
    position: absolute; top: 14px; right: 14px;
    background: rgba(10,14,26,.85);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(212,168,68,.3);
    border-radius: 10px; padding: 6px 12px;
    text-align: center;
}
.reco-score-num {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem; font-weight: 900;
    color: #d4a844; line-height: 1;
    display: block;
}
.reco-score-stars { font-size: .65rem; color: #d4a844; letter-spacing: .05em; }
.reco-body { padding: 20px 22px 22px; }
.reco-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem; font-weight: 700;
    color: #e8e4dc; margin: 0 0 4px;
}
.reco-region { font-size: .78rem; color: #5a6580; margin-bottom: 10px; }
.reco-tagline { font-size: .85rem; color: #8a95aa; line-height: 1.5; margin-bottom: 12px; }
.reco-why {
    background: #131826;
    border-left: 3px solid #d4a844;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px; margin-bottom: 10px;
    font-size: .8rem; color: #8a95aa; line-height: 1.5;
}
.reco-why b { color: #d4a844; }
.reco-social {
    background: #0f1e14;
    border-left: 3px solid #4a9a5a;
    border-radius: 0 8px 8px 0;
    padding: 8px 14px; margin-bottom: 14px;
    font-size: .78rem; color: #6a9a7a;
}
.reco-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.reco-btn-plan {
    display: inline-flex; align-items: center; gap: 6px;
    background: #d4a844; color: #0a0e1a !important;
    border-radius: 10px; padding: 9px 18px;
    font-size: .82rem; font-weight: 700;
    font-family: 'Inter', sans-serif;
    text-decoration: none !important; transition: background .15s;
}
.reco-btn-plan:hover { background: #c49830; }
.reco-btn-video {
    display: inline-flex; align-items: center; gap: 6px;
    background: transparent; border: 1px solid #c4180a;
    color: #c4180a !important; border-radius: 10px;
    padding: 9px 18px; font-size: .82rem; font-weight: 600;
    font-family: 'Inter', sans-serif;
    text-decoration: none !important; transition: all .15s;
}
.reco-btn-video:hover { background: #c4180a; color: #fff !important; }

/* ─ EMPTY STATE ──────────────────────────────────── */
.empty-state {
    text-align: center; padding: 80px 30px;
}
.empty-icon { font-size: 4rem; margin-bottom: 16px; opacity: .4; }
.empty-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem; color: #4a5570; margin-bottom: 8px;
}
.empty-sub { font-size: .88rem; color: #3a4558; max-width: 360px; margin: 0 auto; line-height: 1.6; }

/* ─ STREAMLIT OVERRIDES ──────────────────────────── */
.stButton > button {
    background: #d4a844 !important; color: #0a0e1a !important;
    border: none !important; border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important; font-weight: 700 !important;
    padding: .5rem 1.4rem !important; transition: background .15s !important;
}
.stButton > button:hover { background: #c49830 !important; }
.stSelectSlider > div { color: #e8e4dc !important; }
.stTextInput > div > div > input {
    background: #131826 !important; border: 1px solid #1e2538 !important;
    border-radius: 10px !important; color: #e8e4dc !important;
    font-size: .88rem !important;
}
.stTextInput > div > div > input::placeholder { color: #4a5570 !important; }
.stSelectbox > div > div {
    background: #131826 !important; border: 1px solid #1e2538 !important;
    border-radius: 10px !important; color: #e8e4dc !important;
}
div[data-baseweb="select"] { background: #131826 !important; }
div[data-baseweb="popover"] { background: #131826 !important; }
.stSlider > div > div { color: #e8e4dc !important; }
[data-testid="stMetricValue"] { color: #d4a844 !important; }
hr { border-color: #1e2538 !important; }

/* ─ DIVIDER ──────────────────────────────────────── */
.section-divider {
    height: 1px; background: #1e2538; margin: 0 40px;
}

/* ─ RATING SECTION ──────────────────────────────── */
.notation-section {
    background: #0d1120;
    border-top: 1px solid #1e2538;
    padding: 28px 40px 32px;
    margin-top: 8px;
}
.notation-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem; color: #e8e4dc; margin-bottom: 20px;
}
.notation-card {
    background: #131826;
    border: 1px solid #1e2538;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
    display: flex; align-items: center; gap: 12px;
}
/* FIX: notation image cover */
.notation-img-wrap {
    width: 56px; height: 56px;
    border-radius: 10px;
    overflow: hidden;
    flex-shrink: 0;
    background: #1e2538;
}
.notation-img {
    width: 100%; height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
}
.notation-info { flex: 1; }
.notation-name { font-weight: 600; color: #e8e4dc; font-size: .88rem; margin-bottom: 2px; }
.notation-region { font-size: .72rem; color: #4a5570; }

/* ─ SIMILAR CARD ─────────────────────────────────── */
.sim-card {
    background: #0f1422; border: 1px solid #1e2538;
    border-radius: 14px; overflow: hidden;
    display: flex; transition: border-color .15s;
    margin-bottom: 10px;
}
.sim-card:hover { border-color: #d4a844; }
/* FIX: sim image cover */
.sim-img-wrap {
    width: 90px;
    height: 80px;
    flex-shrink: 0;
    overflow: hidden;
    background: #131826;
}
.sim-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
}
.sim-body { padding: 10px 14px; flex: 1; }
.sim-name { font-family: 'Playfair Display', serif; font-size: .92rem; color: #e8e4dc; font-weight: 700; }
.sim-region { font-size: .7rem; color: #4a5570; margin-bottom: 6px; }
.sim-bar-wrap { background: #1e2538; border-radius: 4px; height: 4px; margin-bottom: 3px; }
.sim-bar-fill { background: linear-gradient(90deg, #d4a844, #f0c860); height: 100%; border-radius: 4px; }
.sim-pct { font-size: .68rem; color: #d4a844; }

/* ─ SCROLL ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e2538; border-radius: 3px; }

/* ─ AUDIO PLAYER ─────────────────────────────────── */
#wm-audio-bar {
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    background: rgba(13,17,32,.94);
    backdrop-filter: blur(20px);
    border: 1px solid #2a3048;
    border-radius: 999px;
    padding: 8px 18px 8px 12px;
    display: flex; align-items: center; gap: 12px;
    box-shadow: 0 8px 40px rgba(0,0,0,.6);
    opacity: 0;
    transition: opacity .4s;
}
#wm-play-btn {
    width: 32px; height: 32px; border-radius: 50%;
    background: #d4a844; border: none; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: .85rem; transition: background .15s; flex-shrink: 0;
    color: #0a0e1a; line-height: 1;
}
#wm-play-btn:hover { background: #c49830; }
#wm-track-name { font-size: .72rem; font-weight: 600; color: #e8e4dc; white-space: nowrap; display: block; }
#wm-track-sub  { font-size: .63rem; color: #4a5570; display: block; }
#wm-eq { display: flex; align-items: flex-end; gap: 2px; height: 16px; }
#wm-eq span { display: block; width: 3px; border-radius: 2px; background: #d4a844; animation: eq-b .8s ease-in-out infinite alternate; }
#wm-eq span:nth-child(2){animation-delay:.15s}
#wm-eq span:nth-child(3){animation-delay:.3s}
#wm-eq span:nth-child(4){animation-delay:.1s}
@keyframes eq-b { from{height:4px} to{height:14px} }
#wm-eq.paused span { animation-play-state: paused; height: 4px; }
#wm-vol-slider {
    -webkit-appearance:none; width:60px; height:3px;
    border-radius:2px; background:#2a3048; outline:none; cursor:pointer;
}
#wm-vol-slider::-webkit-slider-thumb {
    -webkit-appearance:none; width:11px; height:11px;
    border-radius:50%; background:#d4a844; cursor:pointer;
}

/* ─ RESPONSIVE ───────────────────────────────────── */
@media (max-width: 768px) {
    .hero-title { font-size: 2rem; }
    .hero-content { padding: 0 24px 24px; }
    .section-header { padding: 24px 20px 12px; }
    .section-title { font-size: 1.2rem; }
    .dest-card-name { font-size: .9rem; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# DATA & MODEL
# ══════════════════════════════════════════════════════════
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

ASSETS_DIR = Path(__file__).parent / "assets"
IMG_DIR    = ASSETS_DIR / "images" / "destinations"
HERO_DIR   = ASSETS_DIR / "images" / "heroes"
SND_DIR    = ASSETS_DIR / "sounds"

# Placeholder SVG encodé inline
PLACEHOLDER_B64 = (
    "data:image/svg+xml;base64," +
    base64.b64encode(
        b'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500">'
        b'<rect width="800" height="500" fill="#0f1422"/>'
        b'<text x="50%" y="46%" text-anchor="middle" font-size="48" fill="#1e2538">&#9992;</text>'
        b'<text x="50%" y="58%" text-anchor="middle" font-size="16" fill="#2a3048" font-family="sans-serif">Image non disponible</text>'
        b'</svg>'
    ).decode()
)

@st.cache_data
def local_img(path: Path) -> str:
    """Charge une image locale en base64 data-URI. Retourne placeholder si absente."""
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        candidate = path.with_suffix(ext)
        if candidate.exists():
            mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else f"image/{ext[1:]}"
            data = base64.b64encode(candidate.read_bytes()).decode()
            return f"data:{mime};base64,{data}"
    return PLACEHOLDER_B64

def img_url(dest_id: int) -> str:
    return local_img(IMG_DIR / f"dest_{dest_id}")

def hero_img(name: str) -> str:
    return local_img(HERO_DIR / name)


# ══════════════════════════════════════════════════════════
# FONCTIONS AUDIO
# ══════════════════════════════════════════════════════════

@st.cache_data
def load_audio() -> str:
    """Charge le fichier audio local en base64 data-URI."""
    for ext in [".mp3", ".ogg", ".wav"]:
        f = SND_DIR / f"ambient{ext}"
        if f.exists():
            mime = {"mp3":"audio/mpeg","ogg":"audio/ogg","wav":"audio/wav"}[ext[1:]]
            data = base64.b64encode(f.read_bytes()).decode()
            return f"data:{mime};base64,{data}"
    return ""


_audio_src = load_audio()
_audio_tag = f'<source src="{_audio_src}" type="audio/mpeg"/>' if _audio_src else ""

_audio_html = """
<div id="wm-audio-bar">
  <button id="wm-play-btn" onclick="togglePlay()" title="Lecture / Pause">&#9654;</button>
  <div id="wm-track-info">
    <span id="wm-track-name">Ambient Travel Mix</span>
    <span id="wm-track-sub">Musique d'ambiance · WanderMatch</span>
  </div>
  <div id="wm-eq" class="paused">
    <span></span><span></span><span></span><span></span>
  </div>
  <input type="range" id="wm-vol-slider" min="0" max="1" step="0.05" value="0.35"
         oninput="setVol(this.value)" title="Volume"/>
</div>
<audio id="wm-audio" loop>
""" + _audio_tag + """
</audio>
<script>
(function(){
  const audio=document.getElementById('wm-audio');
  const btn=document.getElementById('wm-play-btn');
  const eq=document.getElementById('wm-eq');
  const bar=document.getElementById('wm-audio-bar');
  let started=false;
  function markStarted(){
    started=true; btn.textContent='\u23F8'; eq.classList.remove('paused');
    document.removeEventListener('click',onFirstClick);
    document.removeEventListener('keydown',onFirstClick);
  }
  function onFirstClick(){
    if(started)return;
    audio.muted=false; audio.volume=0.35;
    audio.play().then(markStarted).catch(function(){});
  }
  audio.muted=true; audio.volume=0;
  audio.play().then(function(){
    var v=0;
    var fade=setInterval(function(){
      v=Math.min(v+0.04,0.35);
      audio.volume=v;
      if(v>=0.35){ audio.muted=false; clearInterval(fade); markStarted(); }
    },80);
  }).catch(function(){
    audio.muted=false; audio.volume=0.35;
    document.addEventListener('click',onFirstClick);
    document.addEventListener('keydown',onFirstClick);
  });
  window.togglePlay=function(){
    if(audio.paused){audio.muted=false;audio.volume=0.35;audio.play();btn.textContent='\u23F8';eq.classList.remove('paused');started=true;}
    else{audio.pause();btn.textContent='\u25B6';eq.classList.add('paused');}
  };
  window.setVol=function(v){audio.muted=false;audio.volume=parseFloat(v);};
  bar.style.opacity='0';
  setTimeout(function(){bar.style.opacity='0.92';},600);
})();
</script>
"""

# ══════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════

def yt(name: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote(name + ' travel 4K vlog')}"

def plan(name: str) -> str:
    return f"https://www.google.com/search?q={quote(name + ' voyage conseils incontournables')}"

def stars_str(r: float) -> str:
    f = int(r); h = 1 if r % 1 >= .5 else 0; e = 5 - f - h
    return "★" * f + ("½" if h else "") + "☆" * e

def tags_html(t: str) -> str:
    return "".join(f'<span class="dest-tag">{x.strip()}</span>' for x in t.split("|"))


# ══════════════════════════════════════════════════════════
# CHARGEMENT
# ══════════════════════════════════════════════════════════

ratings_df, dests_df = load_data()
model = load_model()

DEST       = dests_df.set_index("destId").to_dict("index")
ALL_IDS    = dests_df["destId"].tolist()
CONT_EMOJI = {"Asia": "🌏", "Europe": "🌍", "Americas": "🌎", "Africa": "🌍", "Oceania": "🌏"}

# Session state init
for k, v in [("seen", {}), ("recs", []), ("page", "explorer")]:
    if k not in st.session_state:
        st.session_state[k] = v

def set_page(p):
    st.session_state.page = p


# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-logo-text">✈ WanderMatch</div>
      <div class="sb-logo-sub">Recommandation de voyages · IA</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-section">Navigation</div>', unsafe_allow_html=True)

    # Boutons un par ligne
    if st.button("Explorer", use_container_width=True, key="nav_exp"):
        set_page("explorer")
        st.rerun()
    
    badge = "Recommandation" + (f" ({len(st.session_state.recs)})" if st.session_state.recs else "")
    if st.button(badge, use_container_width=True, key="nav_rec"):
        set_page("recs")
        st.rerun()
    
    if st.button("Simulateur", use_container_width=True, key="nav_sim"):  # Changé "Sim." en texte complet
        set_page("sim")
        st.rerun()

    st.markdown('<div class="sb-section" style="margin-top:16px;">Mon profil voyageur</div>', unsafe_allow_html=True)

    seen = st.session_state.seen
    if seen:
        avg = np.mean(list(seen.values()))
        st.markdown(f"""
        <div class="sb-profile-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span style="font-size:.72rem;color:#4a5570;text-transform:uppercase;letter-spacing:.08em;">{len(seen)} destination{'s' if len(seen)!=1 else ''}</span>
            <span style="color:#d4a844;font-weight:700;font-size:.9rem;">{avg:.1f} ★ moy.</span>
          </div>""", unsafe_allow_html=True)
        for did, r in list(seen.items())[:5]:
            name = DEST.get(did, {}).get("name", "")
            st.markdown(f"""
          <div class="sb-dest-item">
            <span class="sb-dest-name">{name}</span>
            <span class="sb-dest-stars">{'★' * int(r)}</span>
          </div>""", unsafe_allow_html=True)
        if len(seen) > 5:
            st.markdown(f'<div style="font-size:.7rem;color:#3a4558;padding-top:6px;">+{len(seen)-5} autre(s)…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if len(seen) >= 2:
            if st.button("Générer mes recommandations", use_container_width=True, key="gen_recs"):
                with st.spinner("Analyse en cours…"):
                    recs = model.predict_for_profile(seen, n=6)
                    for r in recs:
                        info = DEST.get(r["destId"], {})
                        r.update({k: info.get(k, "") for k in ["name", "region", "tagline", "tags", "unsplash_query"]})
                    st.session_state.recs = recs
                    st.session_state.page = "recs"
                st.rerun()

        if st.button("🗑 Réinitialiser profil", use_container_width=True, key="reset_profile"):
            st.session_state.seen = {}
            st.session_state.recs = []
            st.rerun()
    else:
        st.markdown("""
        <div class="sb-profile-card">
          <div style="font-size:.82rem;color:#3a4558;text-align:center;padding:8px 0;">
            Explorez le catalogue<br>et notez vos destinations 
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-section" style="margin-top:16px;">Dataset</div>', unsafe_allow_html=True)
    s = model.get_global_stats()
    st.markdown(f"""
    <div style="padding:0 4px 16px;">
      <div class="sb-stat"><span>Voyageurs</span><span class="sb-stat-val">{s['n_users']}</span></div>
      <div class="sb-stat"><span>Destinations</span><span class="sb-stat-val">{s['n_destinations']}</span></div>
      <div class="sb-stat"><span>Avis collectés</span><span class="sb-stat-val">{s['n_ratings']:,}</span></div>
      <div class="sb-stat" style="border:none"><span>Note moyenne</span><span class="sb-stat-val">{s['mean_rating']} ★</span></div>
    </div>""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════
# PAGE : EXPLORER
# ══════════════════════════════════════════════════════════
if st.session_state.page == "explorer":

    _hero1 = hero_img("hero_explorer")
    st.markdown(f"""
    <div class="hero-section">
      <div class="hero-bg" style="background-image:url('{_hero1}');"></div>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="hero-eyebrow">✈ WanderMatch · Moteur de recommandation</div>
        <div class="hero-title">Votre prochain<br><span>voyage de rêve</span><br>vous attend.</div>
        <div class="hero-sub">Notez vos destinations favorites — notre IA vous révèle celles qui vous correspondent parfaitement.</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header"><span class="section-title">Explorer les destinations</span></div>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 1.5, 1.5])
    with fc1:
        search = st.text_input("", placeholder="Rechercher une destination…",
                               label_visibility="collapsed", key="search_input")
    with fc2:
        conts = ["Tous"] + sorted(dests_df["continent"].unique())
        cont = st.selectbox("Continent", conts, label_visibility="collapsed", key="cont_sel")
    with fc3:
        tag_list = sorted({t for ts in dests_df["tags"] for t in ts.split("|")})
        theme = st.selectbox("Thème", ["Tous"] + tag_list, label_visibility="collapsed", key="theme_sel")

    fd = dests_df.copy()
    if search: fd = fd[fd["name"].str.contains(search, case=False, na=False)]
    if cont != "Tous": fd = fd[fd["continent"] == cont]
    if theme != "Tous": fd = fd[fd["tags"].str.contains(theme, na=False)]

    st.markdown(f'<div style="padding:0 40px 16px;font-size:.8rem;color:#4a5570;">'
                f'{len(fd)} destination{"s" if len(fd)!=1 else ""} · Cliquez sur ➕ pour noter'
                f'</div>', unsafe_allow_html=True)

    n_cols = 4
    fd_rows = [fd.iloc[i:i+n_cols] for i in range(0, len(fd), n_cols)]
    _, pad_r = st.columns([1, 20])
    with pad_r:
        for row_df in fd_rows:
            cols = st.columns(n_cols)
            for col, (_, d) in zip(cols, row_df.iterrows()):
                did = int(d["destId"])
                already = did in st.session_state.seen
                avg_rating = ratings_df[ratings_df["destId"] == did]["rating"].mean()
                n_rev = len(ratings_df[ratings_df["destId"] == did])

                with col:
                    img   = img_url(did)
                    cont_e = CONT_EMOJI.get(d["continent"], "🌐")
                    # FIX: utilisation de .dest-card-img-wrap + .dest-card-img pour cover correct
                    st.markdown(f"""
                    <div class="dest-card">
                      <div class="dest-card-img-wrap">
                        <img class="dest-card-img" src="{img}" alt="{d['name']}" loading="lazy"/>
                      </div>
                      <div class="dest-card-body">
                        <div class="dest-card-name">{d['name']}</div>
                        <div class="dest-card-region">{cont_e} {d['region']}</div>
                        <div class="dest-card-tagline">{d['tagline']}</div>
                        <div style="margin-bottom:8px;">{tags_html(d['tags'])}</div>
                        <div class="dest-card-footer">
                          <span class="dest-avg">⭐ {avg_rating:.1f} ({n_rev} avis)</span>
                          <a href="{yt(d['name'])}" target="_blank" class="btn-yt">▶</a>
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)

                    if already:
                        cur = st.session_state.seen[did]
                        st.markdown(
                            f'<div style="background:#1e3a1a;border:1px solid #2e5a28;border-radius:8px;'
                            f'padding:5px 10px;text-align:center;font-size:.75rem;color:#6abf5a;margin-top:6px;">'
                            f'✓ Noté {cur} ★</div>', unsafe_allow_html=True)
                    else:
                        if st.button(" J'y suis allé", key=f"add_{did}", use_container_width=True):
                            st.session_state.seen[did] = 4.0
                            st.rerun()

    # Section notation
    if st.session_state.seen:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="notation-section">', unsafe_allow_html=True)
        st.markdown('<div class="notation-title">✍️ Ajuste tes notes</div>', unsafe_allow_html=True)

        to_rm = []
        ncols = min(4, len(st.session_state.seen))
        note_cols = st.columns(ncols)
        for i, (did, rating) in enumerate(list(st.session_state.seen.items())):
            info = DEST.get(did, {})
            with note_cols[i % ncols]:
                img_sm = img_url(did)
                # FIX: .notation-img-wrap + .notation-img pour cover
                st.markdown(f"""
                <div class="notation-card">
                  <div class="notation-img-wrap">
                    <img class="notation-img" src="{img_sm}" alt="{info.get('name','')}"/>
                  </div>
                  <div class="notation-info">
                    <div class="notation-name">{info.get('name','')}</div>
                    <div class="notation-region">{info.get('region','')}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
                new_r = st.select_slider(
                    "", options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                    value=rating, format_func=lambda x: f"{x}★",
                    key=f"note_{did}", label_visibility="collapsed")
                st.session_state.seen[did] = new_r
                if st.button("✕ Retirer", key=f"rm_{did}", use_container_width=True):
                    to_rm.append(did)
        for d in to_rm:
            del st.session_state.seen[d]
        if to_rm:
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE : RECOMMANDATIONS
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "recs":

    _hero2 = hero_img("hero_recs")
    st.markdown(f"""
    <div class="hero-section" style="height:320px;">
      <div class="hero-bg" style="background-image:url('{_hero2}');"></div>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="hero-eyebrow">Résultats · Filtrage collaboratif item-item</div>
        <div class="hero-title" style="font-size:2.2rem;">Vos destinations<br><span>sur mesure</span></div>
        <div class="hero-sub">Sélectionnées parmi 8 destinations selon les avis de {model.get_global_stats()['n_users']} voyageurs aux goûts similaires.</div>
      </div>
    </div>""", unsafe_allow_html=True)

    recs = st.session_state.recs

    if not recs:
        st.markdown("""
        <div style="padding:40px;">
          <div class="empty-state">
            <div class="empty-icon">🧳</div>
            <div class="empty-title">Aucune recommandation</div>
            <div class="empty-sub">Notez au moins 2 destinations dans <b>Explorer</b> puis cliquez sur <b>Générer mes recommandations</b> dans la sidebar.</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        avg_pred = np.mean([r["predicted_rating"] for r in recs])
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Destinations suggérées", len(recs))
        mc2.metric("Score moyen prédit", f"{avg_pred:.1f} / 5.0")
        mc3.metric("Basé sur", f"{len(st.session_state.seen)} avis")

        st.markdown(
            '<div class="section-header"><span class="section-title">Vos recommandations</span>'
            f'<span class="section-count">Top {len(recs)}</span></div>',
            unsafe_allow_html=True)

        _, outer_pad_r = st.columns([1, 30])
        with outer_pad_r:
            col_a, col_b = st.columns(2, gap="medium")

            for i, rec in enumerate(recs):
                target = col_a if i % 2 == 0 else col_b
                with target:
                    score = rec["predicted_rating"]
                    img   = img_url(rec["destId"])
                    bc    = rec.get("because_of", [])
                    soc   = rec.get("social_explanation", "")

                    names_bc = " et ".join(f'<b>{b["name"]}</b>' for b in bc[:2]) if bc else ""
                    why_html = (f'<div class="reco-why">💡 Recommandé car similaire à {names_bc} que vous avez aimés</div>'
                                if names_bc else "")
                    soc_html = f'<div class="reco-social">👥 {soc}</div>' if soc else ""

                    st.markdown(f"""
                    <div class="reco-card">
                      <div class="reco-img-wrap">
                        <img class="reco-img" src="{img}" alt="{rec['name']}" loading="lazy"/>
                        <div class="reco-rank-badge">#{i+1} Recommandation</div>
                        <div class="reco-score-badge">
                          <span class="reco-score-num">{score:.1f}</span>
                          <div class="reco-score-stars">{stars_str(score)}</div>
                        </div>
                      </div>
                      <div class="reco-body">
                        <div class="reco-name">{rec['name']}</div>
                        <div class="reco-region">📍 {rec.get('region','')}</div>
                        <div class="reco-tagline">{rec.get('tagline','')}</div>
                        <div style="margin-bottom:12px;">{tags_html(rec.get('tags',''))}</div>
                        {why_html}
                        {soc_html}
                        <div class="reco-actions">
                          <a href="{plan(rec['name'])}" target="_blank" class="reco-btn-plan">🌐 Planifier mon voyage</a>
                          <a href="{yt(rec['name'])}" target="_blank" class="reco-btn-video">▶ Voir vidéos</a>
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE : SIMILARITÉ
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "sim":

    _hero3 = hero_img("hero_sim")
    st.markdown(f"""
    <div class="hero-section" style="height:280px;">
      <div class="hero-bg" style="background-image:url('{_hero3}');"></div>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="hero-title" style="font-size:2rem;">Destinations<br><span>qui se ressemblent</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header"><span class="section-title">Choisir une destination de référence</span></div>',
                unsafe_allow_html=True)

    sc1, sc2 = st.columns([1.5, 2.5], gap="large")

    with sc1:
        ref_id = st.selectbox(
            "", ALL_IDS,
            format_func=lambda x: f"{CONT_EMOJI.get(DEST[x]['continent'], '🌐')} {DEST[x]['name']} · {DEST[x]['region']}",
            label_visibility="collapsed", key="sim_ref")

        ref   = DEST[ref_id]
        img_ref = img_url(ref_id)
        rc    = ratings_df[ratings_df["destId"] == ref_id]["rating"]
        avg_r = rc.mean() if len(rc) else 0

        st.markdown(f"""
        <div class="reco-card">
          <div class="reco-img-wrap">
            <img class="reco-img" src="{img_ref}" alt="{ref['name']}" loading="lazy"/>
          </div>
          <div class="reco-body">
            <div class="reco-name">{ref['name']}</div>
            <div class="reco-region">📍 {ref['region']}</div>
            <div style="margin-bottom:12px;">{tags_html(ref['tags'])}</div>
            <div style="font-size:.82rem;color:#8a95aa;">{ref['tagline']}</div>
            <div style="margin-top:10px;font-size:.78rem;color:#d4a844;">⭐ {avg_r:.1f} · {len(rc)} avis</div>
            <div style="margin-top:14px;">
              <a href="{yt(ref['name'])}" target="_blank" class="reco-btn-video"
                 style="width:100%;justify-content:center;display:flex;">▶ Voir vidéos de {ref['name']}</a>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    with sc2:
        sims = model.get_similar_destinations(ref_id, n=8)
        st.markdown(
            f'<div style="font-family:Playfair Display,serif;font-size:1.1rem;color:#e8e4dc;margin-bottom:16px;">'
            f'Destinations similaires à <span style="color:#d4a844;">{ref["name"]}</span></div>',
            unsafe_allow_html=True)

        for s in sims:
            sinfo   = DEST.get(s["destId"], {})
            sim_pct = int(s["similarity"] * 100)
            sim_img = img_url(s["destId"])

            # FIX: .sim-img-wrap + .sim-img pour cover
            st.markdown(f"""
            <div class="sim-card">
              <div class="sim-img-wrap">
                <img class="sim-img" src="{sim_img}" alt="{sinfo.get('name','')}" loading="lazy"/>
              </div>
              <div class="sim-body">
                <div class="sim-name">{sinfo.get('name','')}</div>
                <div class="sim-region">📍 {sinfo.get('region','')}</div>
                <div class="sim-bar-wrap">
                  <div class="sim-bar-fill" style="width:{sim_pct}%;"></div>
                </div>
                <div class="sim-pct">Similarité : {s['similarity']:.3f} ({sim_pct}%)</div>
              </div>
              <div style="padding:10px 14px;display:flex;align-items:center;">
                <a href="{yt(sinfo.get('name',''))}" target="_blank" class="btn-yt" style="font-size:.85rem;padding:8px 10px;">▶</a>
              </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# AUDIO PLAYER — injection propre via components.html
# Le CSS position:fixed permet au player de flotter sur toute la page
# même depuis l'intérieur d'un iframe
# ══════════════════════════════════════════════════════════
import streamlit.components.v1 as components

_audio_full_html = """
<style>
  /* Remonte le player hors de l'iframe pour qu'il soit visible */
  body { margin:0; background:transparent; overflow:hidden; }
  #wm-audio-bar {
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    background: rgba(13,17,32,.94);
    backdrop-filter: blur(20px);
    border: 1px solid #2a3048;
    border-radius: 999px;
    padding: 8px 18px 8px 12px;
    display: flex; align-items: center; gap: 12px;
    box-shadow: 0 8px 40px rgba(0,0,0,.6);
    font-family: 'Inter', sans-serif;
    opacity: 0; transition: opacity .4s;
  }
  #wm-play-btn {
    width: 32px; height: 32px; border-radius: 50%;
    background: #d4a844; border: none; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: .85rem; flex-shrink: 0; color: #0a0e1a;
  }
  #wm-play-btn:hover { background: #c49830; }
  #wm-track-name { font-size: .72rem; font-weight: 600; color: #e8e4dc; white-space: nowrap; display: block; }
  #wm-track-sub  { font-size: .63rem; color: #4a5570; display: block; }
  #wm-eq { display: flex; align-items: flex-end; gap: 2px; height: 16px; }
  #wm-eq span { display: block; width: 3px; border-radius: 2px; background: #d4a844; animation: eq-b .8s ease-in-out infinite alternate; }
  #wm-eq span:nth-child(2){animation-delay:.15s}
  #wm-eq span:nth-child(3){animation-delay:.3s}
  #wm-eq span:nth-child(4){animation-delay:.1s}
  @keyframes eq-b { from{height:4px} to{height:14px} }
  #wm-eq.paused span { animation-play-state: paused; height: 4px; }
  #wm-vol-slider { -webkit-appearance:none; width:60px; height:3px; border-radius:2px; background:#2a3048; outline:none; cursor:pointer; }
  #wm-vol-slider::-webkit-slider-thumb { -webkit-appearance:none; width:11px; height:11px; border-radius:50%; background:#d4a844; cursor:pointer; }
</style>

<div id="wm-audio-bar">
  <button id="wm-play-btn" onclick="togglePlay()" title="Lecture / Pause">&#9654;</button>
  <div id="wm-track-info">
    <span id="wm-track-name">Ambient Travel Mix</span>
    <span id="wm-track-sub">Musique d'ambiance · WanderMatch</span>
  </div>
  <div id="wm-eq" class="paused">
    <span></span><span></span><span></span><span></span>
  </div>
  <input type="range" id="wm-vol-slider" min="0" max="1" step="0.05" value="0.35"
         oninput="setVol(this.value)" title="Volume"/>
</div>

<audio id="wm-audio" loop>
  <source src=\"""" + _audio_src + """\" type="audio/mpeg"/>
</audio>

<script>
(function(){
  const audio = document.getElementById('wm-audio');
  const btn   = document.getElementById('wm-play-btn');
  const eq    = document.getElementById('wm-eq');
  const bar   = document.getElementById('wm-audio-bar');
  let started = false;

  function markStarted(){
    started = true;
    btn.textContent = '\u23F8';
    eq.classList.remove('paused');
    document.removeEventListener('click', onFirstClick);
    document.removeEventListener('keydown', onFirstClick);
  }
  function onFirstClick(){
    if(started) return;
    audio.muted = false; audio.volume = 0.35;
    audio.play().then(markStarted).catch(function(){});
  }

  // Tentative autoplay muet puis fade-in
  audio.muted = true; audio.volume = 0;
  audio.play().then(function(){
    var v = 0;
    var fade = setInterval(function(){
      v = Math.min(v + 0.04, 0.35);
      audio.volume = v;
      if(v >= 0.35){ audio.muted = false; clearInterval(fade); markStarted(); }
    }, 80);
  }).catch(function(){
    // Autoplay bloqué → on attend un clic
    audio.muted = false; audio.volume = 0.35;
    document.addEventListener('click', onFirstClick);
    document.addEventListener('keydown', onFirstClick);
  });

  window.togglePlay = function(){
    if(audio.paused){
      audio.muted = false; audio.volume = 0.35;
      audio.play();
      btn.textContent = '\u23F8';
      eq.classList.remove('paused');
      started = true;
    } else {
      audio.pause();
      btn.textContent = '\u25B6';
      eq.classList.add('paused');
    }
  };
  window.setVol = function(v){ audio.muted = false; audio.volume = parseFloat(v); };

  setTimeout(function(){ bar.style.opacity = '0.92'; }, 600);
})();
</script>
"""

components.html(_audio_full_html, height=80)