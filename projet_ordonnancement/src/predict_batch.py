import os
import argparse
import joblib
import json
import pandas as pd
from parser_dzn import DznParser

# --- Fonction d'extraction des features ---
def extract_features(instance_path):
    parser = DznParser(instance_path)
    data = parser.get_data()

    dur = data['dur']
    n_activities = len(dur)
    n_resources = data.get('nResources', 0)
    sreq = data.get('sreq', [])
    mastery = data.get('mastery', [])
    n_skills = len(sreq[0]) if sreq else 0
    n_edges = sum(len(p['successors']) for p in data['precedence_graph'].values())

    avg_skills_act = sum(sum(1 for v in row if v) for row in sreq) / n_activities if sreq else 0
    max_skills_act = max((sum(1 for v in row if v) for row in sreq), default=0)

    avg_skills_res = sum(sum(1 for v in row if v) for row in mastery) / n_resources if mastery else 0
    max_skills_res = max((sum(1 for v in row if v) for row in mastery), default=0)

    return [
        n_activities,
        n_resources,
        n_skills,
        min(dur),
        max(dur),
        sum(dur) / len(dur),
        pd.Series(dur).std(),
        n_edges,
        n_edges / (n_activities * (n_activities - 1)) if n_activities > 1 else 0,
        avg_skills_act,
        max_skills_act,
        avg_skills_res,
        max_skills_res,
        0, 0, 0  # spt_flow, lpt_flow, mst_flow par défaut
    ]

# --- Script principal ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=['xgboost', 'randomforest', 'decisiontree'], required=True)
    parser.add_argument('--folder', required=True, help='Chemin vers le dossier contenant les fichiers .dzn')
    args = parser.parse_args()

    model_name = args.model
    folder = args.folder

    # Chargement des modèles
    clf = joblib.load(f"modeles/{model_name}_clf_balanced.pkl")

    reg = joblib.load(f"modeles/{model_name}_reg.pkl")
    le = joblib.load(f"modeles/{model_name}_label_encoder.pkl")

    print(f"\n📂 Prédictions sur les instances dans {folder}\n")
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".dzn"):
            continue
        try:
            path = os.path.join(folder, filename)
            features = extract_features(path)
            print(f"🔢 Features extraites : {features}")

            pred_class = le.inverse_transform(clf.predict([features]))[0]
            pred_flow = reg.predict([features])[0]
            print(f"📄 {filename:<35} → Algorithme : {pred_class:<4} | Flot estimé : {pred_flow:.4f}")
        except Exception as e:
            print(f"⚠️ Erreur sur {filename} : {e}")
