"""
TP0 - Exercice 2 : Word Count sur le corpus Gutenberg (>1 Go)
=============================================================
Téléchargement du corpus :
  https://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2  (~1 Go textes)

  Ou via Python (voir bloc TÉLÉCHARGEMENT ci-dessous) :
    pip install requests tqdm

Configuration Windows recommandée :
  HADOOP_HOME = C:/hadoop       (dossier contenant bin/winutils.exe)
  JAVA_HOME   = C:/Program Files/Java/jdk-11 (ou votre version)
  Mémoire driver : --driver-memory 2g  (voir SparkConf ci-dessous)

Lancer :
  python tp0_gutenberg.py [chemin_du_dossier_textes]

  Exemple :
  python tp0_gutenberg.py C:/gutenberg_texts
"""

import os
import sys
import re
import time
from pyspark import SparkContext, SparkConf

# ─── TÉLÉCHARGEMENT automatique (optionnel) ──────────────────────────────────
def telecharger_echantillon(dossier: str, nb_livres: int = 50):
    """
    Télécharge nb_livres livres depuis le miroir Gutenberg.
    Installe d'abord : pip install requests tqdm
    """
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        print("[ERREUR] Installe d'abord : pip install requests tqdm")
        sys.exit(1)

    os.makedirs(dossier, exist_ok=True)
    BASE_URL = "https://www.gutenberg.org/files/"

    # IDs des 50 livres les plus populaires de Gutenberg
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
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    with open(fichier, "wb") as f:
                        f.write(r.content)
                    break
            except Exception:
                continue
    taille = sum(
        os.path.getsize(os.path.join(dossier, f))
        for f in os.listdir(dossier)
        if f.endswith(".txt")
    )
    print(f"[INFO] Corpus téléchargé : {taille / 1e6:.1f} Mo dans '{dossier}'")

# ─── Configuration Spark (optimisée pour gros volumes sur Windows) ────────────
def creer_spark_context() -> SparkContext:
    conf = SparkConf() \
        .setAppName("Gutenberg_WordCount") \
        .setMaster("local[*]") \
        .set("spark.driver.memory", "2g") \
        .set("spark.executor.memory", "2g") \
        .set("spark.default.parallelism", "8") \
        .set("spark.sql.shuffle.partitions", "8") \
        .set("spark.ui.showConsoleProgress", "true")
    sc = SparkContext(conf=conf)
    sc.setLogLevel("WARN")
    return sc

# ─── Nettoyage de texte Gutenberg ─────────────────────────────────────────────
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

def nettoyer_ligne(ligne: str):
    """
    Map : une ligne de texte → liste de (mot, 1)
    - Minuscules
    - Suppression ponctuation
    - Filtrage stop-words et mots très courts
    - Filtrage des lignes d'en-tête Gutenberg
    """
    ligne = ligne.lower().strip()
    # Ignore les lignes d'en-tête/pied Gutenberg
    if any(tag in ligne for tag in ["gutenberg", "project", "ebook", "charset", "encoding"]):
        return []
    mots = re.findall(r"[a-z']+", ligne)
    return [
        (mot, 1)
        for mot in mots
        if len(mot) > 2 and mot not in STOP_WORDS
    ]

# ─── Programme principal ──────────────────────────────────────────────────────
def main():
    # Dossier des textes (argument CLI ou valeur par défaut)
    if len(sys.argv) > 1:
        dossier_textes = sys.argv[1]
    else:
        dossier_textes = "gutenberg_texts"

    # Téléchargement si le dossier n'existe pas ou est vide
    if not os.path.exists(dossier_textes) or \
       not any(f.endswith(".txt") for f in os.listdir(dossier_textes)):
        print(f"[INFO] Dossier '{dossier_textes}' vide. Lancement du téléchargement...")
        telecharger_echantillon(dossier_textes, nb_livres=50)

    # Vérification taille corpus
    taille = sum(
        os.path.getsize(os.path.join(dossier_textes, f))
        for f in os.listdir(dossier_textes)
        if f.endswith(".txt")
    )
    print(f"\n[INFO] Corpus : {taille / 1e6:.1f} Mo — "
          f"{len([f for f in os.listdir(dossier_textes) if f.endswith('.txt')])} fichiers\n")

    # ── Initialisation Spark ──────────────────────────────────────────────────
    sc = creer_spark_context()

    debut = time.time()

    # ── Étape 1 : Lecture du corpus (wildcard → tous les .txt) ───────────────
    chemin = os.path.join(os.path.abspath(dossier_textes), "*.txt")
    rdd_lignes = sc.textFile(chemin)
    print(f"[INFO] Partitions : {rdd_lignes.getNumPartitions()}")

    # ── Étape 2 : MAP — (mot, 1) pour chaque mot valide ─────────────────────
    rdd_paires = rdd_lignes.flatMap(nettoyer_ligne)

    # ── Étape 3 : REDUCE — sommer par clé (combine local + réseau) ───────────
    rdd_counts = rdd_paires.reduceByKey(lambda a, b: a + b)

    # ── Étape 4 : Tri décroissant ─────────────────────────────────────────────
    rdd_top = rdd_counts.sortBy(lambda x: x[1], ascending=False)

    # ── Action : récupérer les 50 mots les plus fréquents ────────────────────
    top_50 = rdd_top.take(50)
    duree  = time.time() - debut

    # ── Affichage des résultats ───────────────────────────────────────────────
    print("\n" + "═" * 50)
    print("   TOP 50 mots — Corpus Gutenberg")
    print("═" * 50)
    for rang, (mot, count) in enumerate(top_50, 1):
        barre = "█" * min(40, count // 500)
        print(f"  {rang:>3}. {mot:<20} {count:>8,}  {barre}")

    print(f"\n[INFO] Traitement terminé en {duree:.2f}s")
    print(f"[INFO] Vocabulaire total : {rdd_counts.count():,} mots uniques")

    # ── Sauvegarde des résultats complets ─────────────────────────────────────
    sortie = "gutenberg_wordcount_output"
    if os.path.exists(sortie):
        import shutil; shutil.rmtree(sortie)
    rdd_top.saveAsTextFile(sortie)
    print(f"[INFO] Résultats complets sauvegardés dans : {sortie}/\n")

    sc.stop()
    print("[OK] SparkContext arrêté proprement.")

if __name__ == "__main__":
    main()
