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

# On force Spark à utiliser exactement le même interpréteur Python
# que celui qui exécute ce script. Sans ça, sur Windows, Spark cherche
# une commande "python" qui pointe vers le Microsoft Store → crash.
os.environ["PYSPARK_PYTHON"]        = sys.executable  # pour les workers Spark
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable  # pour le driver Spark
os.environ["SPARK_LOCAL_IP"]        = "127.0.0.1"     # évite les erreurs réseau en local

import re        # expressions régulières pour extraire les mots
import glob      # recherche de fichiers par pattern (*.txt)
import time      # mesure du temps d'exécution
from pyspark import SparkContext, SparkConf


# ─── TÉLÉCHARGEMENT automatique du corpus ────────────────────────────────────
def telecharger_echantillon(dossier: str, nb_livres: int = 50):
    """
    Télécharge nb_livres livres depuis le miroir public du projet Gutenberg.
    Les livres sont enregistrés sous forme de fichiers .txt dans 'dossier'.
    Si un fichier existe déjà, il est ignoré (reprise possible).
    """
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        print("[ERREUR] Installe d'abord : pip install requests tqdm")
        sys.exit(1)

    os.makedirs(dossier, exist_ok=True)  # crée le dossier si inexistant
    BASE_URL = "https://www.gutenberg.org/files/"

    # IDs des 50 livres les plus populaires du projet Gutenberg
    # (Pride and Prejudice, Frankenstein, Alice, Sherlock Holmes, etc.)
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
            continue  # déjà téléchargé, on passe

        # Gutenberg propose plusieurs suffixes selon l'encodage du fichier
        for ext in [".txt", "-0.txt", "-8.txt"]:
            url = f"{BASE_URL}{book_id}/{book_id}{ext}"
            try:
                import requests as req
                r = req.get(url, timeout=15)
                if r.status_code == 200:
                    with open(fichier, "wb") as f:
                        f.write(r.content)
                    break  # fichier trouvé et sauvegardé, on arrête les tentatives
            except Exception:
                continue  # tentative échouée, on essaie le suffixe suivant

    # Calcul de la taille totale du corpus téléchargé
    taille = sum(
        os.path.getsize(os.path.join(dossier, f))
        for f in os.listdir(dossier) if f.endswith(".txt")
    )
    print(f"[INFO] Corpus téléchargé : {taille / 1e6:.1f} Mo dans '{dossier}'")


# ─── Configuration du SparkContext ───────────────────────────────────────────
def creer_spark_context() -> SparkContext:
    """
    Crée et retourne un SparkContext configuré pour une exécution locale.
    local[*] utilise tous les cœurs disponibles de la machine.
    """
    conf = (
        SparkConf()
        .setAppName("Gutenberg_WordCount")   # nom affiché dans l'UI Spark
        .setMaster("local[*]")               # mode local, tous les cœurs
        .set("spark.driver.memory", "2g")    # mémoire allouée au driver
        .set("spark.executor.memory", "2g")  # mémoire allouée aux executors
        .set("spark.default.parallelism", "8")       # nb de partitions par défaut
        .set("spark.sql.shuffle.partitions", "8")    # nb de partitions après shuffle
        .set("spark.ui.showConsoleProgress", "true") # affiche la progression dans le terminal
    )
    sc = SparkContext(conf=conf)
    sc.setLogLevel("WARN")  # masque les logs INFO/DEBUG pour plus de lisibilité
    return sc


# ─── Liste des stop-words à ignorer ──────────────────────────────────────────
# Les stop-words sont des mots grammaticaux très fréquents mais sans valeur
# sémantique (articles, pronoms, prépositions, auxiliaires...).
# Les exclure permet de faire ressortir les mots porteurs de sens.
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


# ─── Fonction MAP : transforme une ligne en paires (mot, 1) ──────────────────
def nettoyer_ligne(ligne: str):
    """
    Prend une ligne de texte brut et retourne une liste de paires (mot, 1).

    Étapes du nettoyage :
      1. Mise en minuscules et suppression des espaces en début/fin
      2. Exclusion des lignes d'en-tête/pied de page Gutenberg
      3. Extraction des mots (lettres a-z et apostrophes uniquement)
      4. Filtrage : mots de plus de 2 lettres, absents des stop-words
    """
    ligne = ligne.lower().strip()

    # On ignore les lignes liées aux métadonnées Gutenberg
    # (ex: "Project Gutenberg's Pride and Prejudice", "Encoding: UTF-8")
    if any(tag in ligne for tag in ["gutenberg", "project", "ebook", "charset", "encoding"]):
        return []

    # Extraction des mots : on garde uniquement les séquences de lettres
    # et apostrophes (pour gérer les contractions comme "don't", "it's")
    mots = re.findall(r"[a-z']+", ligne)

    # On ne garde que les mots significatifs :
    # - longueur > 2 (élimine "a", "an", "to"... non couverts par stop-words)
    # - absent de la liste des stop-words
    return [(mot, 1) for mot in mots if len(mot) > 2 and mot not in STOP_WORDS]


# ─── Lecture des fichiers texte en Python pur ─────────────────────────────────
def lire_fichiers_python(dossier: str):
    """
    Lit tous les fichiers .txt du dossier et retourne toutes leurs lignes
    dans une seule liste Python.

    On utilise Python pur (glob + open) plutôt que sc.textFile() de Spark
    car sc.textFile() passe par Hadoop, qui requiert winutils.exe sur Windows.
    Cette approche évite l'erreur UnsatisfiedLinkError liée à NativeIO.
    """
    pattern = os.path.join(os.path.abspath(dossier), "*.txt")
    fichiers = glob.glob(pattern)  # liste tous les .txt du dossier
    if not fichiers:
        print(f"[ERREUR] Aucun fichier .txt trouvé dans : {dossier}")
        sys.exit(1)

    print(f"[INFO] Lecture de {len(fichiers)} fichiers...")
    lignes = []
    for chemin_fichier in fichiers:
        try:
            # errors="ignore" : on saute les caractères non-UTF8 (encodages anciens)
            with open(chemin_fichier, encoding="utf-8", errors="ignore") as fh:
                lignes.extend(fh.readlines())
        except Exception as e:
            print(f"[WARN] {chemin_fichier} : {e}")  # fichier illisible, on continue
    return lignes


# ─── Programme principal ──────────────────────────────────────────────────────
def main():

    # Vérification de la version Python : Python 3.13 est incompatible avec
    # PySpark sur Windows à cause d'un changement dans la gestion des sockets
    # (OSError WinError 10038). On bloque l'exécution pour éviter un crash.
    if sys.version_info >= (3, 13):
        print("[ERREUR] Python 3.13 incompatible avec PySpark sur Windows.")
        print("         Lance le script avec : C:\\Python311\\python.exe tp0_gutenberg.py")
        sys.exit(1)

    # Dossier contenant les textes (argument CLI ou valeur par défaut)
    dossier_textes = sys.argv[1] if len(sys.argv) > 1 else "gutenberg_texts"

    # Si le dossier est absent ou vide, on lance le téléchargement automatique
    if not os.path.exists(dossier_textes) or \
       not any(f.endswith(".txt") for f in os.listdir(dossier_textes)):
        print(f"[INFO] Dossier '{dossier_textes}' vide. Téléchargement...")
        telecharger_echantillon(dossier_textes, nb_livres=50)

    # Affichage des informations sur le corpus
    fichiers_txt = [f for f in os.listdir(dossier_textes) if f.endswith(".txt")]
    taille = sum(os.path.getsize(os.path.join(dossier_textes, f)) for f in fichiers_txt)
    print(f"\n[INFO] Corpus : {taille / 1e6:.1f} Mo — {len(fichiers_txt)} fichiers")
    print(f"[INFO] Python : {sys.executable}  (v{sys.version.split()[0]})\n")

    # ── Initialisation de Spark ───────────────────────────────────────────────
    sc = creer_spark_context()
    debut = time.time()  # démarrage du chronomètre

    # ── ÉTAPE 1 : Chargement et distribution des données ──────────────────────
    # On lit les fichiers en Python pur, puis on distribue les lignes
    # en 8 partitions Spark avec parallelize().
    # Chaque partition sera traitée indépendamment par un worker Spark.
    lignes = lire_fichiers_python(dossier_textes)
    rdd_lignes = sc.parallelize(lignes, numSlices=8)
    print(f"[INFO] {len(lignes):,} lignes — {rdd_lignes.getNumPartitions()} partitions Spark\n")

    # ── ÉTAPE 2 : MAP — extraction des mots ──────────────────────────────────
    # flatMap applique nettoyer_ligne() à chaque ligne et aplatit les résultats.
    # Résultat : un RDD de paires (mot, 1) — une paire par occurrence de mot.
    # Exemple : "Hello world hello" → [("hello", 1), ("world", 1), ("hello", 1)]
    rdd_paires = rdd_lignes.flatMap(nettoyer_ligne)

    # ── ÉTAPE 3 : REDUCE — agrégation des comptages par mot ──────────────────
    # reduceByKey regroupe toutes les paires ayant la même clé (même mot)
    # et les combine avec la fonction lambda : addition des compteurs.
    # Chaque partition effectue d'abord une réduction locale (combiner),
    # puis les résultats sont agrégés globalement (shuffle réseau).
    # Exemple : [("hello",1),("world",1),("hello",1)] → [("hello",2),("world",1)]
    rdd_counts = rdd_paires.reduceByKey(lambda a, b: a + b)

    # ── ÉTAPE 4 : Collecte et tri ─────────────────────────────────────────────
    # collect() ramène tous les résultats du cluster vers le driver (Python).
    # On trie ensuite en mémoire Python par ordre décroissant de fréquence.
    # Note : pour un très grand corpus, on préférerait takeOrdered() ou sortBy()
    # pour ne rapatrier que le top N sans tout charger en mémoire.
    tous_les_mots = rdd_counts.collect()
    tous_les_mots.sort(key=lambda x: x[1], reverse=True)

    duree = time.time() - debut  # temps total de traitement Spark
    top_50 = tous_les_mots[:50]  # on extrait le top 50

    # ── Affichage du classement ───────────────────────────────────────────────
    print("\n" + "═" * 55)
    print("   TOP 50 mots — Corpus Gutenberg")
    print("═" * 55)
    for rang, (mot, count) in enumerate(top_50, 1):
        # Barre proportionnelle : 1 bloc par 500 occurrences, max 40 blocs
        barre = "█" * min(40, count // 500)
        print(f"  {rang:>3}. {mot:<20} {count:>8,}  {barre}")

    print(f"\n[INFO] Traitement terminé en {duree:.2f}s")
    print(f"[INFO] Vocabulaire total : {len(tous_les_mots):,} mots uniques")

    # ── Sauvegarde des résultats complets ─────────────────────────────────────
    # On écrit en Python pur (pas saveAsTextFile) pour éviter Hadoop/winutils.
    # Format : une ligne par mot → "mot\tcount"
    sortie_dir = "gutenberg_wordcount_output"
    os.makedirs(sortie_dir, exist_ok=True)
    sortie_fichier = os.path.join(sortie_dir, "results.txt")
    with open(sortie_fichier, "w", encoding="utf-8") as f:
        for mot, count in tous_les_mots:
            f.write(f"{mot}\t{count}\n")
    print(f"[INFO] Résultats sauvegardés dans : {sortie_fichier}\n")

    # Arrêt propre du SparkContext — libère les ressources JVM
    sc.stop()
    print("[OK] SparkContext arrêté proprement.")


if __name__ == "__main__":
    main()