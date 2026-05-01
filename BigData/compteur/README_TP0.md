# TP0 — MapReduce avec PySpark sur Windows
## Installation rapide (5 étapes)

### 1. Python & PySpark
```bash
pip install pyspark requests tqdm
```

### 2. Java (obligatoire pour Spark)
Télécharge JDK 11 : https://adoptium.net/
- Installe, puis note le chemin (ex: `C:\Program Files\Eclipse Adoptium\jdk-11...`)
- Ajoute dans les variables d'environnement :
  ```
  JAVA_HOME = C:\Program Files\Eclipse Adoptium\jdk-11...
  ```

### 3. winutils.exe (obligatoire sur Windows)
Spark a besoin de l'utilitaire Hadoop pour Windows.
- Télécharge `winutils.exe` pour Hadoop 3.x :
  https://github.com/cdarlint/winutils/tree/master/hadoop-3.3.5/bin
- Crée le dossier `C:\hadoop\bin\` et mets-y `winutils.exe`
- Ajoute la variable d'environnement :
  ```
  HADOOP_HOME = C:\hadoop
  ```

### 4. Relancer le terminal (pour que les variables soient prises en compte)

### 5. Vérification
```bash
python -c "from pyspark import SparkContext; sc = SparkContext('local'); print('OK'); sc.stop()"
```
Si tu vois `OK` sans erreur, c'est bon !

---

## Exercice 1 — Word Count (warm-up)
```bash
python tp0_wordcount.py
```
Le script contient le texte d'exemple intégré, pas besoin de fichier externe.

**Ce que montre le script :**
- `parallelize()` → créer un RDD depuis une liste Python
- `flatMap(mapper)` → la phase MAP : (ligne → liste de paires (mot, 1))
- `groupByKey()` → SHUFFLE explicite pour visualiser le regroupement
- `reduceByKey()` → la phase REDUCE optimisée (combinaison locale avant shuffle)
- Comparaison `groupByKey` vs `reduceByKey` expliquée dans la sortie

---

## Exercice 2 — Corpus Gutenberg (>1 Go)

```bash
# Avec téléchargement automatique (50 livres, ~150 Mo)
python tp0_gutenberg.py

# Avec un dossier de textes existant
python tp0_gutenberg.py C:\chemin\vers\mes\textes
```

**Pour atteindre 1 Go :** Change `nb_livres=50` en `nb_livres=500` dans `telecharger_echantillon()`.

**Ce que montre le script :**
- `sc.textFile("dossier/*.txt")` → lecture parallèle de milliers de fichiers
- Nettoyage des en-têtes Gutenberg
- Pipeline MapReduce complet sur gros volume
- `saveAsTextFile()` → sauvegarde distribuée du résultat
- Métriques : temps de traitement, nombre de mots uniques

---

## Résultats attendus (exercice 2)
```
  1. said               45,000  ████████
  2. one                38,000  ███████
  3. man                32,000  ██████
  4. time               29,000  █████
  5. know               27,000  █████
  ...
```

---

## Problèmes fréquents sur Windows

| Erreur | Solution |
|--------|----------|
| `JAVA_HOME not set` | Vérifier la variable d'environnement JAVA_HOME |
| `winutils.exe not found` | Placer winutils.exe dans C:\hadoop\bin\ |
| `Address already in use` | Spark UI port 4040 occupé → normal, Spark utilise 4041, 4042... |
| `OutOfMemoryError` | Augmenter `spark.driver.memory` à `4g` dans SparkConf |
| `Permission denied` sur le dossier de sortie | Supprimer manuellement le dossier `gutenberg_wordcount_output/` avant de relancer |
