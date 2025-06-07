import json
import pandas as pd

file_path = 'projet_ordonnancement/modeles/data/classification_data.json'

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    targets = data.get('target', [])
    
    if targets:
        target_series = pd.Series(targets)
        unique_targets = list(target_series.unique())
        target_counts = target_series.value_counts().to_dict()
        print(f"Cibles uniques trouvées : {unique_targets}")
        print(f"Compte des cibles : {target_counts}")
    else:
        print("Le champ 'target' est introuvable ou vide dans le fichier JSON.")

except FileNotFoundError:
    print(f"Erreur : Le fichier {file_path} n'a pas été trouvé.")
except json.JSONDecodeError:
    print(f"Erreur : Impossible de décoder le JSON du fichier {file_path}.")
except Exception as e:
    print(f"Une erreur inattendue est survenue : {e}")

