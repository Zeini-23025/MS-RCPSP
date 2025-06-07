#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour afficher les statistiques des méthodes
"""

import os
import pandas as pd

def afficher_statistiques_methodes(results_dir):
    """
    Affiche les statistiques sur le pourcentage de solutions pour chaque méthode
    
    Args:
        results_dir (str): Chemin vers le répertoire des résultats
    """
    # Charger les résultats de comparaison
    comparison_file = os.path.join(results_dir, 'comparison_results.csv')
    if not os.path.exists(comparison_file):
        print(f"Fichier de comparaison non trouvé: {comparison_file}")
        return
    
    try:
        # Charger les données
        df = pd.read_csv(comparison_file)
        
        # Compter le nombre d'instances pour chaque meilleur algorithme
        algo_counts = df['best_algorithms'].value_counts()
        total_instances = len(df)
        
        print("\n" + "="*60)
        print("STATISTIQUES DES MÉTHODES".center(60))
        print("="*60)
        
        # Afficher les résultats sous forme de tableau
        print(f"{'Méthode':<15} | {'Nombre d\'instances':<20} | {'Pourcentage':<15}")
        print("-"*60)
        
        for algo, count in algo_counts.items():
            percentage = (count / total_instances) * 100
            print(f"{algo:<15} | {count:<20} | {percentage:.2f}%")
        
        print("="*60)
        
        # Méthode la plus efficace
        best_algo = algo_counts.idxmax()
        print(f"La méthode la plus efficace est {best_algo} avec {algo_counts[best_algo]} instances ({(algo_counts[best_algo]/total_instances)*100:.2f}%)")
        print("="*60 + "\n")
        
        # Création d'un graphique à barres
        try:
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(10, 6))
            algo_counts.plot(kind='bar', color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            plt.title('Nombre d\'instances où chaque algorithme est le meilleur')
            plt.xlabel('Algorithme')
            plt.ylabel('Nombre d\'instances')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Ajouter les pourcentages sur les barres
            for i, v in enumerate(algo_counts):
                percentage = (v / total_instances) * 100
                plt.text(i, v + 0.1, f"{percentage:.1f}%", ha='center')
            
            plt.savefig(os.path.join(results_dir, 'statistiques_methodes.png'))
            print(f"Graphique enregistré dans {os.path.join(results_dir, 'statistiques_methodes.png')}")
            plt.close()
        except Exception as e:
            print(f"Impossible de créer le graphique: {e}")
        
    except Exception as e:
        print(f"Erreur lors de l'analyse des statistiques: {e}")

if __name__ == "__main__":
    # Répertoire des résultats
    results_dir = "./resultats"
    
    # Afficher les statistiques
    afficher_statistiques_methodes(results_dir)