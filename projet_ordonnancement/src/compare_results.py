#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour comparer les résultats et sélectionner le meilleur algorithme
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def compare_results(results_dir):
    """
    Compare les résultats des différents algorithmes et sélectionne le meilleur
    
    Args:
        results_dir (str): Chemin vers le répertoire des résultats
    
    Returns:
        dict: Résultats de la comparaison
    """
    # Récupérer tous les fichiers de résultats Ford-Fulkerson
    ff_dir = os.path.join(results_dir, 'ford_fulkerson')
    if not os.path.isdir(ff_dir):
        raise FileNotFoundError(f"Le dossier '{ff_dir}' n'existe pas. Veuillez vérifier le chemin.")
    ff_files = [f for f in os.listdir(ff_dir) if f.endswith('.json')]
    
    # Initialiser les résultats
    comparison = {
        'instances': [],
        'best_algorithms': [],
        'spt_flow': [],
        'lpt_flow': [],
        'mst_flow': [],
        'best_flow': []
    }
    
    # Parcourir tous les fichiers
    for ff_file in ff_files:
        with open(os.path.join(ff_dir, ff_file), 'r') as f:
            result = json.load(f)
            
            # Ajouter les résultats à la comparaison
            comparison['instances'].append(result['instance'])
            comparison['best_algorithms'].append(result['best_algorithm'])
            comparison['spt_flow'].append(result['results']['SPT']['max_flow'])
            comparison['lpt_flow'].append(result['results']['LPT']['max_flow'])
            comparison['mst_flow'].append(result['results']['MST']['max_flow'])
            comparison['best_flow'].append(result['best_max_flow'])
    
    # Calculer les statistiques
    algo_counts = {}
    for algo in comparison['best_algorithms']:
        if algo in algo_counts:
            algo_counts[algo] += 1
        else:
            algo_counts[algo] = 1
    
    # Créer un DataFrame pour faciliter l'analyse
    df = pd.DataFrame(comparison)
    
    # Enregistrer les résultats
    df.to_csv(os.path.join(results_dir, 'comparison_results.csv'), index=False)
    
    # Créer des visualisations
    create_visualizations(df, results_dir)
    
    return {
        'comparison': comparison,
        'algo_counts': algo_counts,
        'dataframe': df
    }

def create_visualizations(df, results_dir):
    """
    Crée des visualisations pour les résultats
    
    Args:
        df (DataFrame): DataFrame contenant les résultats
        results_dir (str): Chemin vers le répertoire des résultats
    """
    # Créer le répertoire pour les visualisations
    viz_dir = os.path.join(results_dir, 'visualisations')
    os.makedirs(viz_dir, exist_ok=True)
    
    # 1. Histogramme des meilleurs algorithmes
    plt.figure(figsize=(10, 6))
    algo_counts = df['best_algorithms'].value_counts()
    algo_counts.plot(kind='bar', color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    plt.title('Nombre d\'instances où chaque algorithme est le meilleur')
    plt.xlabel('Algorithme')
    plt.ylabel('Nombre d\'instances')
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'best_algorithms_histogram.png'))
    plt.close()
    
    # 2. Comparaison des flots maximaux pour chaque instance
    plt.figure(figsize=(12, 8))
    
    # Créer un indice pour les instances
    instance_indices = range(len(df))
    
    # Tracer les flots maximaux pour chaque algorithme
    bar_width = 0.25
    plt.bar([i - bar_width for i in instance_indices], df['spt_flow'], bar_width, label='SPT', color='#1f77b4')
    plt.bar(instance_indices, df['lpt_flow'], bar_width, label='LPT', color='#ff7f0e')
    plt.bar([i + bar_width for i in instance_indices], df['mst_flow'], bar_width, label='MST', color='#2ca02c')
    
    plt.title('Comparaison des flots maximaux pour chaque instance')
    plt.xlabel('Instance')
    plt.ylabel('Flot maximal')
    plt.xticks(instance_indices, df['instances'], rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'max_flow_comparison.png'))
    plt.close()
    
    # 3. Boxplot des flots maximaux pour chaque algorithme
    plt.figure(figsize=(10, 6))
    data = [df['spt_flow'], df['lpt_flow'], df['mst_flow']]
    plt.boxplot(data, labels=['SPT', 'LPT', 'MST'])
    plt.title('Distribution des flots maximaux pour chaque algorithme')
    plt.ylabel('Flot maximal')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'max_flow_boxplot.png'))
    plt.close()

def generate_summary_report(comparison_results, results_dir):
    """
    Génère un rapport de synthèse des résultats
    
    Args:
        comparison_results (dict): Résultats de la comparaison
        results_dir (str): Chemin vers le répertoire des résultats
    """
    df = comparison_results['dataframe']
    algo_counts = comparison_results['algo_counts']
    
    # Calculer des statistiques supplémentaires
    total_instances = len(df)
    algo_percentages = {algo: count / total_instances * 100 for algo, count in algo_counts.items()}
    
    avg_flows = {
        'SPT': df['spt_flow'].mean(),
        'LPT': df['lpt_flow'].mean(),
        'MST': df['mst_flow'].mean()
    }
    
    # Générer le rapport
    report = f"""# Rapport de synthèse des résultats

## Résumé global

Nombre total d'instances analysées: {total_instances}

### Répartition des meilleurs algorithmes

| Algorithme | Nombre d'instances | Pourcentage |
|------------|-------------------|------------|
"""
    
    for algo, count in algo_counts.items():
        report += f"| {algo} | {count} | {algo_percentages[algo]:.2f}% |\n"
    
    report += f"""
### Flots maximaux moyens

| Algorithme | Flot maximal moyen |
|------------|-------------------|
| SPT | {avg_flows['SPT']:.2f} |
| LPT | {avg_flows['LPT']:.2f} |
| MST | {avg_flows['MST']:.2f} |

## Détails par instance

| Instance | Meilleur algorithme | Flot maximal | SPT | LPT | MST |
|----------|---------------------|-------------|-----|-----|-----|
"""
    
    for _, row in df.iterrows():
        report += f"| {row['instances']} | {row['best_algorithms']} | {row['best_flow']} | {row['spt_flow']} | {row['lpt_flow']} | {row['mst_flow']} |\n"
    
    report += """
## Conclusion

"""
    
    # Déterminer l'algorithme globalement le meilleur
    best_overall = max(algo_counts.keys(), key=lambda k: algo_counts[k])
    report += f"L'algorithme {best_overall} est globalement le plus performant, étant le meilleur pour {algo_counts[best_overall]} instances sur {total_instances} ({algo_percentages[best_overall]:.2f}%).\n\n"
    
    # Ajouter des observations sur les performances relatives
    best_avg = max(avg_flows.keys(), key=lambda k: avg_flows[k])
    report += f"En termes de flot maximal moyen, l'algorithme {best_avg} obtient les meilleurs résultats avec une moyenne de {avg_flows[best_avg]:.2f}.\n\n"
    
    report += "Ces résultats suggèrent que pour ce type de problèmes d'ordonnancement, l'utilisation de l'algorithme "
    
    if best_overall == best_avg:
        report += f"{best_overall} est généralement la meilleure approche."
    else:
        report += f"{best_overall} est généralement la meilleure approche, bien que {best_avg} puisse offrir de meilleurs résultats en moyenne."
    
    # Enregistrer le rapport
    with open(os.path.join(results_dir, 'summary_report.md'), 'w') as f:
        f.write(report)
    
    return report

if __name__ == "__main__":
    # Comparer les résultats
    results_dir = "./resultats"
    
    print("Comparaison des résultats...")
    comparison_results = compare_results(results_dir)
    
    print("Génération du rapport de synthèse...")
    generate_summary_report(comparison_results, results_dir)
    
    print("Terminé !")
