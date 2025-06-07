import os
import json
import pandas as pd
from compare_results import compare_results
from parser_dzn import DznParser

INSTANCES_DIR = "./instances"
RESULTS_FILE = "./resultats/comparison_results.csv"
OUTPUT_DIR = "./modeles/data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

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

    return {
        "n_activities": n_activities,
        "n_resources": n_resources,
        "n_skills": n_skills,
        "min_duration": min(dur),
        "max_duration": max(dur),
        "avg_duration": sum(dur) / len(dur),
        "std_duration": pd.Series(dur).std(),
        "n_precedence_edges": n_edges,
        "precedence_density": n_edges / (n_activities * (n_activities - 1)) if n_activities > 1 else 0,
        "avg_skills_per_activity": avg_skills_act,
        "max_skills_per_activity": max_skills_act,
        "avg_skills_per_resource": avg_skills_res,
        "max_skills_per_resource": max_skills_res,
    }

if __name__ == "__main__":
    print("Préparation des données d'entraînement...")
    comparison_result = compare_results("./resultats")
    df_res = comparison_result['dataframe']
    df_res.to_csv(RESULTS_FILE, index=False)

    features = []
    classification_labels = []
    regression_targets = []

    for i, row in df_res.iterrows():
        instance_name = row['instances']
        instance_path = os.path.join(INSTANCES_DIR, instance_name)
        if not os.path.exists(instance_path):
            continue
        print(f"Extraction des caractéristiques pour {instance_name}...")
        feat = extract_features(instance_path)
        feat['spt_flow'] = row['spt_flow']
        feat['lpt_flow'] = row['lpt_flow']
        feat['mst_flow'] = row['mst_flow']

        features.append(feat)
        classification_labels.append(row['best_algorithms'])
        regression_targets.append(row['best_flow'])

    df = pd.DataFrame(features)
    df.to_csv(os.path.join(OUTPUT_DIR, "training_data.csv"), index=False)

    classification_data = {
        "features": df.values.tolist(),
        "target": classification_labels
    }

    regression_data = {
        "features": df.values.tolist(),
        "target": regression_targets
    }

    with open(os.path.join(OUTPUT_DIR, "classification_data.json"), 'w') as f:
        json.dump(classification_data, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "regression_data.json"), 'w') as f:
        json.dump(regression_data, f, indent=2)

    print(f"Données d'entraînement préparées avec {len(features)} instances.")
    print(f"Caractéristiques extraites: {list(df.columns)}")
