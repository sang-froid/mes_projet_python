"""
TP0 - Exercice 1 : Word Count avec MapReduce en PySpark
========================================================
Prérequis Windows :
  pip install pyspark
  Télécharger winutils.exe : https://github.com/cdarlint/winutils
  Placer dans C:/hadoop/bin/ et définir HADOOP_HOME=C:/hadoop

Lancer :
  python tp0_wordcount.py
"""

from pyspark import SparkContext, SparkConf
import re
import sys

# ─── Configuration Spark ────────────────────────────────────────────────────
conf = SparkConf() \
    .setAppName("WordCount_MapReduce") \
    .setMaster("local[*]")          # utilise tous les cœurs disponibles

sc = SparkContext(conf=conf)
sc.setLogLevel("WARN")              # réduit le bruit dans la console

# ─── Données d'entrée ────────────────────────────────────────────────────────
# Option A : texte inline (warm-up)
texte = [
    "hello world hello",
    "world of hadoop and spark",
    "hello spark hello hadoop",
    "map reduce is powerful",
]

# Option B : fichier local → décommentez la ligne ci-dessous
# rdd_raw = sc.textFile("mon_fichier.txt")

# ─── Étape 0 : Paralléliser les données (créer un RDD) ───────────────────────
rdd_raw = sc.parallelize(texte)
print(f"\n[INFO] Nombre de partitions : {rdd_raw.getNumPartitions()}")
print(f"[INFO] Nombre de lignes      : {rdd_raw.count()}\n")

# ─── Étape 1 : MAP — émettre (mot, 1) pour chaque mot ───────────────────────
# flatMap : une ligne → plusieurs paires (mot, 1)
def mapper(line):
    """Nettoie la ligne et émet (mot, 1) pour chaque mot."""
    mots = re.findall(r"[a-zA-ZÀ-ÿ]+", line.lower())
    return [(mot, 1) for mot in mots]

rdd_mapped = rdd_raw.flatMap(mapper)

# Aperçu des paires émises par le mapper
print("=== Sortie MAP (10 premières paires) ===")
for paire in rdd_mapped.take(10):
    print(f"  {paire}")

# ─── Étape 2 : SHUFFLE + GROUP — regrouper par clé ───────────────────────────
# groupByKey() est explicite mais peu efficace sur gros volumes
# (utiliser reduceByKey en production — voir ci-dessous)
rdd_grouped = rdd_mapped.groupByKey()

print("\n=== Sortie SHUFFLE/GROUP (5 premières clés) ===")
for mot, valeurs in rdd_grouped.take(5):
    print(f"  '{mot}' → {list(valeurs)}")

# ─── Étape 3 : REDUCE — sommer les 1 par clé ─────────────────────────────────
# Version CORRECTE et efficace : reduceByKey (combinaison locale avant shuffle)
rdd_counts = rdd_mapped.reduceByKey(lambda a, b: a + b)

# ─── Étape 4 : Tri décroissant et affichage ───────────────────────────────────
rdd_sorted = rdd_counts.sortBy(lambda x: x[1], ascending=False)

print("\n=== Résultats Word Count (tous les mots) ===")
for mot, count in rdd_sorted.collect():
    print(f"  {mot:<20} {count}")

# ─── Comparaison : groupByKey vs reduceByKey ─────────────────────────────────
print("\n=== Comparaison groupByKey vs reduceByKey ===")
print("  groupByKey : transfert ALL les valeurs sur le réseau, puis réduit")
print("  reduceByKey: combine localement avant shuffle → BEAUCOUP plus rapide")
print("  → Toujours préférer reduceByKey sur gros volumes !\n")

# ─── Étape 5 (bonus) : version one-liner façon fonctionnelle ─────────────────
print("=== Version condensée (one-liner) ===")
resultat = (
    sc.parallelize(texte)
      .flatMap(lambda line: re.findall(r"[a-zA-ZÀ-ÿ]+", line.lower()))
      .map(lambda mot: (mot, 1))
      .reduceByKey(lambda a, b: a + b)
      .sortBy(lambda x: x[1], ascending=False)
      .collect()
)
for mot, count in resultat:
    print(f"  {mot:<20} {count}")

sc.stop()
print("\n[OK] SparkContext arrêté proprement.")
