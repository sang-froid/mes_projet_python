"""
TP0 - Exercice 2 : Word Count sur le corpus Gutenberg
======================================================
LANCER AVEC PYTHON 3.11 (pas 3.13) :
  C:\Python311\python.exe tp0_gutenberg.py [dossier_textes]

Dépendances (à installer avec Python 3.11) :
  C:\Python311\python.exe -m pip install pyspark requests tqdm
"""

import os
import sys

# ─── Forcer Spark à utiliser CE Python (le même qui lance le script) ──────────
os.environ["PYSPARK_PYTHON"]        = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["SPARK_LOCAL_IP"]        = "127.0.0.1"

import re
import glob
import time
from pyspark import SparkContext, SparkConf


# ─── TÉLÉCHARGEMENT automatique ──────────────────────────────────────────────
def telecharger_echantillon(dossier: str, nb_livres: int = 50):
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        print("[ERREUR] Installe d'abord : pip install requests tqdm")
        sys.exit(1)

    os.makedirs(dossier, exist_ok=True)
    BASE_URL = "https://www.gutenberg.org/files/"

    livres_populaires = [
        1342, 84, 11, 1661, 74, 1952, 2701, 46, 1400, 16328,
        98,   174, 345, 514, 2542, 1260, 844, 4300, 5200, 6130,
        215,  2600, 1232, 6761, 768, 1184, 76, 43,  25344, 30254,
        55,   120, 829, 33, 2814, 160, 730, 1727, 3207, 1251,
        786,  244, 1998, 2097, 23, 158, 1080, 526, 3296, 863
    ][:nb_livres]

    print(f"[INFO] Téléchargement de {nb_livres} livres dans '{dossier}'...")
    for book_id in tqdm(livres_populaires, desc="Téléchargement"):
        fichier = os.path.join(dossier, f"{book_id}.txt")
        if os.path.exists(fichier):
            continue
        for ext in [".txt", "-0.txt", "-8.txt"]:
            url = f"{BASE_URL}{book_id}/{book_id}{ext}"
            try:
                import requests as req
                r = req.get(url, timeout=15)
                if r.status_code == 200:
                    with open(fichier, "wb") as f:
                        f.write(r.content)
                    break
            except Exception:
                continue

    taille = sum(
        os.path.getsize(os.path.join(dossier, f))
        for f in os.listdir(dossier) if f.endswith(".txt")
    )
    print(f"[INFO] Corpus téléchargé : {taille / 1e6:.1f} Mo dans '{dossier}'")


# ─── Configuration Spark ──────────────────────────────────────────────────────
def creer_spark_context() -> SparkContext:
    conf = (
        SparkConf()
        .setAppName("Gutenberg_WordCount")
        .setMaster("local[*]")
        .set("spark.driver.memory", "2g")
        .set("spark.executor.memory", "2g")
        .set("spark.default.parallelism", "8")
        .set("spark.sql.shuffle.partitions", "8")
        .set("spark.ui.showConsoleProgress", "true")
    )
    sc = SparkContext(conf=conf)
    sc.setLogLevel("WARN")
    return sc


# ─── Stop-words ───────────────────────────────────────────────────────────────
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "is", "was", "are", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can",
    "i", "he", "she", "it", "we", "they", "you", "my", "his",
    "her", "our", "their", "its", "your", "not", "no", "as", "by",
    "from", "this", "that", "which", "who", "whom", "what", "when",
    "where", "how", "if", "so", "up", "out", "about", "into", "than",
    "then", "s", "t", "don", "project", "gutenberg", "mr", "mrs",
}


# ─── MAP : ligne → liste de (mot, 1) ─────────────────────────────────────────
def nettoyer_ligne(ligne: str):
    ligne = ligne.lower().strip()
    if any(tag in ligne for tag in ["gutenberg", "project", "ebook", "charset", "encoding"]):
        return []
    mots = re.findall(r"[a-z']+", ligne)
    return [(mot, 1) for mot in mots if len(mot) > 2 and mot not in STOP_WORDS]


# ─── Lecture fichiers en Python pur (évite NativeIO / winutils) ──────────────
def lire_fichiers_python(dossier: str):
    pattern = os.path.join(os.path.abspath(dossier), "*.txt")
    fichiers = glob.glob(pattern)
    if not fichiers:
        print(f"[ERREUR] Aucun fichier .txt trouvé dans : {dossier}")
        sys.exit(1)
    print(f"[INFO] Lecture de {len(fichiers)} fichiers...")
    lignes = []
    for chemin_fichier in fichiers:
        try:
            with open(chemin_fichier, encoding="utf-8", errors="ignore") as fh:
                lignes.extend(fh.readlines())
        except Exception as e:
            print(f"[WARN] {chemin_fichier} : {e}")
    return lignes


# ─── Programme principal ──────────────────────────────────────────────────────
def main():
    # Vérification version Python
    if sys.version_info >= (3, 13):
        print("[ERREUR] Python 3.13 incompatible avec PySpark sur Windows.")
        print("         Lance le script avec : C:\\Python311\\python.exe tp0_gutenberg.py")
        sys.exit(1)

    dossier_textes = sys.argv[1] if len(sys.argv) > 1 else "gutenberg_texts"

    # Téléchargement si nécessaire
    if not os.path.exists(dossier_textes) or \
       not any(f.endswith(".txt") for f in os.listdir(dossier_textes)):
        print(f"[INFO] Dossier '{dossier_textes}' vide. Téléchargement...")
        telecharger_echantillon(dossier_textes, nb_livres=50)

    fichiers_txt = [f for f in os.listdir(dossier_textes) if f.endswith(".txt")]
    taille = sum(os.path.getsize(os.path.join(dossier_textes, f)) for f in fichiers_txt)
    print(f"\n[INFO] Corpus : {taille / 1e6:.1f} Mo — {len(fichiers_txt)} fichiers")
    print(f"[INFO] Python : {sys.executable}  (v{sys.version.split()[0]})\n")

    # ── Init Spark ────────────────────────────────────────────────────────────
    sc = creer_spark_context()
    debut = time.time()

    # ── Étape 1 : Lecture Python pur → parallelize ────────────────────────────
    lignes = lire_fichiers_python(dossier_textes)
    rdd_lignes = sc.parallelize(lignes, numSlices=8)
    print(f"[INFO] {len(lignes):,} lignes — {rdd_lignes.getNumPartitions()} partitions Spark\n")

    # ── Étape 2 : MAP — (mot, 1) pour chaque mot valide ─────────────────────
    rdd_paires = rdd_lignes.flatMap(nettoyer_ligne)

    # ── Étape 3 : REDUCE — sommer par clé ────────────────────────────────────
    rdd_counts = rdd_paires.reduceByKey(lambda a, b: a + b)

    # ── Étape 4 : collect() + tri Python ──────────────────────────────────────
    tous_les_mots = rdd_counts.collect()
    tous_les_mots.sort(key=lambda x: x[1], reverse=True)

    duree = time.time() - debut
    top_50 = tous_les_mots[:50]

    # ── Affichage ─────────────────────────────────────────────────────────────
    print("\n" + "═" * 55)
    print("   TOP 50 mots — Corpus Gutenberg")
    print("═" * 55)
    for rang, (mot, count) in enumerate(top_50, 1):
        barre = "█" * min(40, count // 500)
        print(f"  {rang:>3}. {mot:<20} {count:>8,}  {barre}")

    print(f"\n[INFO] Traitement terminé en {duree:.2f}s")
    print(f"[INFO] Vocabulaire total : {len(tous_les_mots):,} mots uniques")

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    sortie_dir = "gutenberg_wordcount_output"
    os.makedirs(sortie_dir, exist_ok=True)
    sortie_fichier = os.path.join(sortie_dir, "results.txt")
    with open(sortie_fichier, "w", encoding="utf-8") as f:
        for mot, count in tous_les_mots:
            f.write(f"{mot}\t{count}\n")
    print(f"[INFO] Résultats sauvegardés dans : {sortie_fichier}\n")

    sc.stop()
    print("[OK] SparkContext arrêté proprement.")


if __name__ == "__main__":
    main()