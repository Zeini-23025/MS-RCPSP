import os
import json
import joblib
import argparse
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.utils.class_weight import compute_class_weight
import xgboost as xgb

def train_classification_models(data_dir, models_dir, algo):
    print(f"\n🔄 Entraînement du modèle de classification ({algo}) avec pondération des classes...")
    with open(os.path.join(data_dir, 'classification_data.json'), 'r') as f:
        data = json.load(f)

    X_class = pd.DataFrame(data['features'])
    y_class_labels = data['target']

    le = LabelEncoder()
    y_class = le.fit_transform(y_class_labels)
    # Sauvegarder l'encoder AVANT de potentiellement modifier y_class pour le calcul des poids
    joblib.dump(le, os.path.join(models_dir, f"{algo}_label_encoder.pkl"))
    print(f"Classes trouvées par LabelEncoder : {list(le.classes_)}")

    X_train, X_test, y_train, y_test = train_test_split(X_class, y_class, test_size=0.2, random_state=42, stratify=y_class) # Ajout de stratify

    # Calculer les poids des classes pour gérer le déséquilibre
    # Utiliser les labels originaux encodés (y_class) pour le calcul des poids
    classes = np.unique(y_train)
    weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_train)
    class_weights_dict = dict(zip(classes, weights))
    print(f"Poids des classes calculés : {class_weights_dict}")

    if algo == 'xgboost':
        # Pour XGBoost, on utilise sample_weight dans la méthode fit
        model = xgb.XGBClassifier(random_state=42)
        # Créer le tableau sample_weight pour l'ensemble d'entraînement
        sample_weights_train = np.array([class_weights_dict[label] for label in y_train])
        model.fit(X_train, y_train, sample_weight=sample_weights_train)
    elif algo == 'randomforest':
        # RandomForest et DecisionTree peuvent prendre class_weight='balanced' directement
        model = RandomForestClassifier(random_state=42, class_weight='balanced')
        model.fit(X_train, y_train)
    elif algo == 'decisiontree':
        model = DecisionTreeClassifier(random_state=42, class_weight='balanced')
        model.fit(X_train, y_train)
    else:
        raise ValueError("Modèle non supporté")

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    # Utiliser les labels décodés pour le rapport de classification pour plus de clarté
    report = classification_report(le.inverse_transform(y_test), le.inverse_transform(y_pred), output_dict=True)

    # Sauvegarder le modèle entraîné
    joblib.dump(model, os.path.join(models_dir, f"{algo}_clf_balanced.pkl")) # Nouveau nom pour le modèle équilibré
    # Sauvegarder les résultats
    results_path = os.path.join(models_dir, f"{algo}_classification_results_balanced.json") # Nouveau nom pour les résultats
    with open(results_path, 'w') as f:
        json.dump({"accuracy": acc, "report": report}, f, indent=2)

    print(f"✅ Classification ({algo}, équilibré) - Accuracy: {acc:.4f}")
    print(f"📄 Rapport de classification sauvegardé dans {results_path}")

def train_regression_models(data_dir, models_dir, algo):
    # La régression n'est pas affectée par le déséquilibre des classes de la même manière
    # On garde l'entraînement original pour la régression
    print(f"\n🔄 Entraînement du modèle de régression ({algo})...")
    with open(os.path.join(data_dir, 'regression_data.json'), 'r') as f:
        data = json.load(f)

    X_reg = pd.DataFrame(data['features'])
    y_reg = data['target']

    X_train, X_test, y_train, y_test = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

    if algo == 'xgboost':
        model = xgb.XGBRegressor(random_state=42)
    elif algo == 'randomforest':
        model = RandomForestRegressor(random_state=42)
    elif algo == 'decisiontree':
        model = DecisionTreeRegressor(random_state=42)
    else:
        raise ValueError("Modèle non supporté")

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Sauvegarder le modèle de régression (pas besoin de renommer)
    joblib.dump(model, os.path.join(models_dir, f"{algo}_reg.pkl"))
    # Sauvegarder les résultats de régression (pas besoin de renommer)
    results_path = os.path.join(models_dir, f"{algo}_regression_results.json")
    with open(results_path, 'w') as f:
        json.dump({"mse": mse, "r2": r2}, f, indent=2)

    print(f"✅ Régression ({algo}) - MSE: {mse:.4f}, R2: {r2:.4f}")
    print(f"📄 Résultats de régression sauvegardés dans {results_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=['xgboost', 'randomforest', 'decisiontree'], required=True)
    args = parser.parse_args()

    # Utiliser des chemins absolus pour plus de robustesse
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir) # Remonter d'un niveau pour être à la racine du projet
    data_dir = os.path.join(project_root, "modeles", "data")
    models_dir = os.path.join(project_root, "modeles")
    os.makedirs(models_dir, exist_ok=True)

    print(f"📂 Répertoire des données : {data_dir}")
    print(f"📂 Répertoire des modèles : {models_dir}")

    train_classification_models(data_dir, models_dir, algo=args.model)
    train_regression_models(data_dir, models_dir, algo=args.model)

