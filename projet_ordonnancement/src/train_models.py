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
import xgboost as xgb

def train_classification_models(data_dir, models_dir, algo):
    with open(os.path.join(data_dir, 'classification_data.json'), 'r') as f:
        data = json.load(f)

    X_class = pd.DataFrame(data['features'])
    y_class = data['target']

    le = LabelEncoder()
    y_class = le.fit_transform(y_class)
    joblib.dump(le, os.path.join(models_dir, f"{algo}_label_encoder.pkl"))

    X_train, X_test, y_train, y_test = train_test_split(X_class, y_class, test_size=0.2, random_state=42)

    if algo == 'xgboost':
        model = xgb.XGBClassifier(random_state=42)
    elif algo == 'randomforest':
        model = RandomForestClassifier(random_state=42)
    elif algo == 'decisiontree':
        model = DecisionTreeClassifier(random_state=42)
    else:
        raise ValueError("Modèle non supporté")

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    joblib.dump(model, os.path.join(models_dir, f"{algo}_clf.pkl"))
    with open(os.path.join(models_dir, f"{algo}_classification_results.json"), 'w') as f:
        json.dump({"accuracy": acc, "report": report}, f, indent=2)

    print(f"✅ Classification ({algo}) - Accuracy: {acc:.4f}")

def train_regression_models(data_dir, models_dir, algo):
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

    joblib.dump(model, os.path.join(models_dir, f"{algo}_reg.pkl"))
    with open(os.path.join(models_dir, f"{algo}_regression_results.json"), 'w') as f:
        json.dump({"mse": mse, "r2": r2}, f, indent=2)

    print(f"✅ Régression ({algo}) - MSE: {mse:.4f}, R2: {r2:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=['xgboost', 'randomforest', 'decisiontree'], required=True)
    args = parser.parse_args()

    data_dir = "./modeles/data"
    models_dir = "./modeles"
    os.makedirs(models_dir, exist_ok=True)

    train_classification_models(data_dir, models_dir, algo=args.model)
    train_regression_models(data_dir, models_dir, algo=args.model)
