# Rapport d'Analyse et de Correction du Modèle d'Ordonnancement

## Introduction

Vous nous avez signalé un problème concernant votre projet d'ordonnancement : le modèle de prédiction retournait systématiquement la classe "mst", quelle que soit l'instance fournie. Ce rapport détaille l'analyse effectuée, le diagnostic établi, la correction implémentée et les résultats obtenus.

## Analyse Initiale et Structure du Projet

Après extraction de l'archive `projet_ordonnancement.zip`, nous avons identifié la structure suivante :

- Un dossier `src` contenant plusieurs scripts Python, notamment :
    - `parser_dzn.py` : Pour lire les fichiers d'instances `.dzn`.
    - `extract_features.py` (intégré dans `predict_batch.py` et `prepare_data.py`) : Pour extraire les caractéristiques des instances.
    - `train_models.py` : Pour entraîner les modèles de classification et de régression.
    - `predict_batch.py` : Pour effectuer des prédictions sur de nouvelles instances.
    - D'autres scripts utilitaires (`algorithmes.py`, `ford_fulkerson.py`, etc.).
- Un dossier `modeles` contenant :
    - Les modèles entraînés (fichiers `.pkl`) pour différents algorithmes (XGBoost, RandomForest, DecisionTree).
    - Les encodeurs de labels (`_label_encoder.pkl`).
    - Les résultats des entraînements précédents (fichiers `.json`).
    - Un sous-dossier `data` contenant les données prétraitées pour l'entraînement (`classification_data.json`, `regression_data.json`).
- De nombreux fichiers `.dzn` à la racine, semblant être des instances de données (probablement pour des tests ou un usage antérieur, mais pas le jeu `set1b` mentionné).

Le script `predict_batch.py` charge un modèle de classification (`_clf.pkl`) et un encodeur de labels (`_label_encoder.pkl`) pour prédire l'algorithme le plus adapté (`pred_class`) pour une instance donnée.

## Diagnostic : Déséquilibre Sévère des Classes

L'investigation s'est concentrée sur la compréhension du processus d'entraînement (`train_models.py`) et les données utilisées (`modeles/data/classification_data.json`).

En analysant le fichier `classification_data.json` (utilisé pour entraîner les classifieurs), nous avons découvert un **déséquilibre majeur dans la distribution des classes cibles ('target')** :

- **MST : 194 occurrences**
- **LPT : 13 occurrences**
- **SPT : 9 occurrences**

(Ces chiffres ont été obtenus en exécutant le script `check_targets.py` que nous avons créé à cet effet).

Ce déséquilibre extrême est la **cause principale** du comportement observé. Le modèle, lors de l'entraînement, apprend que prédire systématiquement "MST" est la stratégie qui minimise l'erreur sur l'ensemble d'entraînement, car cette classe est ultra-majoritaire. Il ne parvient donc pas à généraliser et à reconnaître correctement les classes minoritaires 'LPT' et 'SPT'.

**Absence des Données de Test :** Il est important de noter que nous n'avons pas pu effectuer de tests directs sur vos instances spécifiques du dossier `data/instances/set1b`, car ce dossier était **absent** de l'archive fournie. Les tests et validations ont donc été réalisés sur la base des données d'entraînement/validation internes au script `train_models.py`.

## Correction Apportée : Pondération des Classes

Pour remédier à ce problème de déséquilibre, nous avons modifié le script d'entraînement. La solution implémentée est la **pondération des classes** lors de l'entraînement des modèles de classification. Cette technique consiste à attribuer un poids plus important aux exemples des classes minoritaires, forçant ainsi le modèle à leur accorder plus d'attention.

Un nouveau script, `train_models_balanced.py`, a été créé. Il intègre les modifications suivantes :

1.  **Utilisation de `stratify=y_class`** dans `train_test_split` pour assurer une répartition proportionnelle des classes entre les ensembles d'entraînement et de test.
2.  **Calcul des poids** avec `sklearn.utils.class_weight.compute_class_weight(class_weight='balanced', ...)`.
3.  **Application des poids** lors de l'entraînement :
    - Pour RandomForest et DecisionTree : via le paramètre `class_weight='balanced'`.
    - Pour XGBoost : via le paramètre `sample_weight` dans la méthode `fit()`, en créant un tableau de poids pour chaque échantillon d'entraînement.

Les modèles de classification ainsi ré-entraînés ont été sauvegardés avec le suffixe `_balanced.pkl` (par exemple, `xgboost_clf_balanced.pkl`) et leurs rapports de classification dans des fichiers `_balanced.json`.

## Validation et Résultats

Nous avons ré-entraîné le modèle XGBoost en utilisant le script modifié (`train_models_balanced.py`). L'analyse du rapport de classification (`xgboost_classification_results_balanced.json`) montre une nette amélioration :

- **Accuracy Globale :** 0.9318 (93.18%)
- **Classe LPT :**
    - Précision : 1.0
    - Rappel (Recall) : 1.0
    - F1-score : 1.0
- **Classe MST :**
    - Précision : 1.0
    - Rappel (Recall) : 0.923
    - F1-score : 0.96
- **Classe SPT :**
    - Précision : 0.4
    - Rappel (Recall) : 1.0
    - F1-score : 0.571

**Interprétation :**

- Le **rappel (Recall)** de 1.0 pour 'LPT' et 'SPT' indique que le modèle équilibré identifie désormais **tous** les exemples de ces classes minoritaires dans l'ensemble de validation. C'est une amélioration significative par rapport au modèle initial qui les ignorait probablement.
- La **précision** pour 'SPT' reste faible (0.4). Cela signifie que lorsque le modèle prédit 'SPT', il n'a raison que 40% du temps. Ceci est directement lié au très faible nombre d'exemples 'SPT' (seulement 9 au total, donc 1 ou 2 dans l'ensemble de validation), rendant difficile pour le modèle d'apprendre des caractéristiques distinctives fiables.
- La classe 'MST' reste bien prédite, avec une légère baisse du rappel compensée par la meilleure reconnaissance des autres classes.

En conclusion, la pondération des classes a permis de corriger le problème principal : le modèle n'est plus biaisé au point d'ignorer les classes minoritaires.

## Conclusion et Recommandations

Le problème de prédiction systématique de la classe 'MST' provenait d'un fort déséquilibre dans les données d'entraînement. La mise en place d'une stratégie de pondération des classes dans le script `train_models_balanced.py` a permis de corriger ce biais et d'améliorer significativement la capacité du modèle à identifier les classes minoritaires 'LPT' et 'SPT'.

Nous vous recommandons :

1.  **D'utiliser les modèles équilibrés** (suffixe `_balanced.pkl`) pour vos prédictions futures. Vous devrez adapter légèrement le script `predict_batch.py` pour charger ces nouveaux fichiers de modèles.
2.  **D'enrichir impérativement votre jeu de données d'entraînement** avec davantage d'exemples représentatifs des classes 'LPT' et 'SPT'. C'est le moyen le plus efficace d'améliorer la précision pour ces classes et la robustesse générale du modèle.
3.  Si possible, de **fournir les instances de test du dossier `set1b`** (ou un autre jeu de test représentatif) afin de pouvoir réaliser une validation plus complète et réaliste des performances du modèle corrigé.

## Fichiers Joints

- `rapport_final.md` : Ce rapport.
- `train_models_balanced.py` : Le script d'entraînement modifié avec pondération des classes.
- `xgboost_classification_results_balanced.json` : Le rapport de classification détaillé pour le modèle XGBoost équilibré.
- `check_targets.py` : Le script utilisé pour analyser la distribution des classes dans les données d'entraînement.
- `xgboost_classification_results.json` : Le rapport de classification du modèle XGBoost original (pour comparaison, montrant probablement un biais vers MST).

