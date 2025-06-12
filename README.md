# Guide d'utilisation du système d'ordonnancement

Ce dossier contient un ensemble complet d'outils pour appliquer les algorithmes SPT, LPT et MST sur des instances de problèmes d'ordonnancement, puis utiliser Ford-Fulkerson pour déterminer le meilleur algorithme .

## Structure du dossier

```
projet_ordonnancement/
├── instances/                  # Dossier contenant les fichiers d'instances .dzn
│   └── exemple.dzn            # Exemple d'instance fourni
├── src/                        # Dossier contenant les scripts source
│   ├── parser_dzn.py          # Script pour parser les fichiers .dzn
│   ├── algorithmes.py         # Implémentation des algorithmes SPT, LPT et MST
│   ├── ford_fulkerson.py      # Implémentation de l'algorithme de Ford-Fulkerson
│   ├── compare_results.py     # Script pour comparer les résultats et sélectionner le meilleur algorithme
│   
│
├── resultats/                  # Dossier contenant les résultats des algorithmes
│   ├── spt/                   # Résultats de l'algorithme SPT
│   ├── lpt/                   # Résultats de l'algorithme LPT
│   ├── mst/                   # Résultats de l'algorithme MST
│   ├── ford_fulkerson/        # Résultats de l'algorithme de Ford-Fulkerson
│   ├── visualisations/        # Visualisations des résultats
│   ├── comparison_results.csv # Résultats de la comparaison des algorithmes
│   └── summary_report.md      # Rapport de synthèse des résultats
```

## Prérequis

Pour exécuter les scripts, vous devez avoir installé les packages Python suivants :
- numpy
- pandas
- matplotlib
- networkx
- scikit-learn
- xgboost

Vous pouvez les installer avec la commande :
```
pip install numpy pandas matplotlib networkx scikit-learn xgboost
```

## Utilisation

### 1. Ajouter des instances

Placez vos fichiers d'instances au format .dzn dans le dossier `instances/`. Pour que le système fonctionne correctement, vous devez avoir au moins 5-10 instances différentes.

### 2. Appliquer les algorithmes SPT, LPT et MST

Exécutez le script `algorithmes.py` pour appliquer les algorithmes SPT, LPT et MST sur toutes les instances :
```
python src/algorithmes.py
```

Les résultats seront enregistrés dans les dossiers `resultats/spt/`, `resultats/lpt/` et `resultats/mst/`.

### 3. Appliquer Ford-Fulkerson

Exécutez le script `ford_fulkerson.py` pour appliquer l'algorithme de Ford-Fulkerson sur les résultats des algorithmes SPT, LPT et MST :
```
python src/ford_fulkerson.py
```

Les résultats seront enregistrés dans le dossier `resultats/ford_fulkerson/`.

### 4. Comparer les résultats

Exécutez le script `compare_results.py` pour comparer les résultats et sélectionner le meilleur algorithme pour chaque instance :
```
python src/compare_results.py
```

Les résultats de la comparaison seront enregistrés dans le fichier `resultats/comparison_results.csv` et un rapport de synthèse sera généré dans le fichier `resultats/summary_report.md`.

## Personnalisation

Vous pouvez personnaliser les paramètres des algorithmes  en modifiant les scripts correspondants dans le dossier `src/`.

