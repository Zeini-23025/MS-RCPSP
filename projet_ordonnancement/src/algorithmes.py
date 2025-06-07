#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour implémenter les algorithmes SPT, LPT et MST
"""

import os
import json
import networkx as nx
from parser_dzn import DznParser, parse_all_instances

class Algorithmes:
    """
    Classe pour implémenter les algorithmes SPT, LPT et MST
    """
    def __init__(self, instance_data):
        """
        Initialise les algorithmes avec les données d'une instance
        
        Args:
            instance_data (dict): Données de l'instance
        """
        self.data = instance_data
        self.activities = list(range(1, self.data['nActs'] + 1))
        self.durations = self.data['dur']
        self.precedence_graph = self.data['precedence_graph']
        
        # Vérification de la cohérence des indices
        print(f"Nombre d'activités: {self.data['nActs']}")
        print(f"Longueur du tableau de durées: {len(self.durations)}")
        print(f"Premières durées: {self.durations[:5]}")
    
    def spt(self):
        """
        Algorithme Shortest Processing Time (SPT)
        Ordonnance les activités par ordre croissant de durée
        
        Returns:
            list: Liste des activités ordonnées selon SPT
        """
        # Filtrer les activités avec durée > 0 (ignorer les activités fictives)
        # Attention: les indices des activités commencent à 1, mais les indices de la liste durations commencent à 0
        valid_activities = [a for a in self.activities if self.durations[a-1] > 0]
        
        # Trier les activités par durée croissante
        sorted_activities = sorted(valid_activities, key=lambda a: self.durations[a-1])
        
        # Réordonner en respectant les contraintes de précédence
        ordered_activities = self._respect_precedence(sorted_activities)
        
        print(f"Activités ordonnées selon SPT: {ordered_activities}")
        return ordered_activities
    
    def lpt(self):
        """
        Algorithme Longest Processing Time (LPT)
        Ordonnance les activités par ordre décroissant de durée
        
        Returns:
            list: Liste des activités ordonnées selon LPT
        """
        # Filtrer les activités avec durée > 0 (ignorer les activités fictives)
        # Attention: les indices des activités commencent à 1, mais les indices de la liste durations commencent à 0
        valid_activities = [a for a in self.activities if self.durations[a-1] > 0]
        
        # Trier les activités par durée décroissante
        sorted_activities = sorted(valid_activities, key=lambda a: self.durations[a-1], reverse=True)
        
        # Réordonner en respectant les contraintes de précédence
        ordered_activities = self._respect_precedence(sorted_activities)
        
        print(f"Activités ordonnées selon LPT: {ordered_activities}")
        return ordered_activities
    
    def mst(self):
        """
        Algorithme Minimum Spanning Tree (MST)
        Construit un arbre couvrant minimal à partir du graphe de précédence
        
        Returns:
            list: Liste des activités ordonnées selon MST
        """
        # Créer un graphe non orienté pour MST
        G = nx.Graph()
        
        # Ajouter les nœuds (activités)
        for activity in self.activities:
            # Ne pas ajouter l'activité fictive 1 (durée 0) au graphe
            if self.durations[activity-1] > 0:
                G.add_node(activity, weight=self.durations[activity-1])
        
        # Ajouter les arêtes avec poids (durée combinée des activités)
        edge_added = False  # Pour vérifier si au moins une arête a été ajoutée
        for activity in self.activities:
            if activity in self.precedence_graph and self.durations[activity-1] > 0:
                for successor in self.precedence_graph[activity]['successors']:
                    if self.durations[successor-1] > 0:  # Ne pas ajouter d'arêtes vers des activités fictives
                        # Poids basé sur la somme des durées
                        weight = self.durations[activity-1] + self.durations[successor-1]
                        G.add_edge(activity, successor, weight=weight)
                        edge_added = True
        
        # Si aucune arête n'a été ajoutée, utiliser une approche alternative
        if not edge_added or len(G.edges()) == 0:
            print("Aucune arête dans le graphe MST, utilisation d'une approche alternative")
            return self._alternative_mst()
        
        # Calculer l'arbre couvrant minimal
        try:
            # Si le graphe est connexe, calculer MST normalement
            if nx.is_connected(G):
                mst = nx.minimum_spanning_tree(G)
                
                # Trouver une racine appropriée (préférer l'activité avec le plus petit indice)
                root = min(G.nodes())
                
                # Parcourir l'arbre en largeur
                ordered_activities = list(nx.bfs_tree(mst, source=root).nodes())
                
                # Filtrer les activités avec durée > 0 (devrait déjà être fait)
                ordered_activities = [a for a in ordered_activities if self.durations[a-1] > 0]
                
                # Réordonner en respectant les contraintes de précédence
                ordered_activities = self._respect_precedence(ordered_activities)
                
                print(f"Activités ordonnées selon MST: {ordered_activities}")
                return ordered_activities
            else:
                # Si le graphe n'est pas connexe, utiliser une approche alternative
                print("Le graphe MST n'est pas connexe, utilisation d'une approche alternative")
                return self._alternative_mst()
                
        except nx.NetworkXException as e:
            # En cas d'erreur, utiliser une approche alternative
            print(f"Erreur MST: {e}. Utilisation d'une approche alternative")
            return self._alternative_mst()
    
    def _alternative_mst(self):
        """
        Méthode alternative quand MST ne peut pas être calculé
        
        Returns:
            list: Liste des activités ordonnées
        """
        # Créer un graphe orienté pour calculer le chemin critique
        dag = nx.DiGraph()
        
        # Ajouter les nœuds et arcs de précédence
        for activity in self.activities:
            if self.durations[activity-1] > 0:  # Ne pas ajouter les activités fictives
                dag.add_node(activity, duration=self.durations[activity-1])
                
        # Ajouter les arcs
        for activity in self.activities:
            if activity in self.precedence_graph and self.durations[activity-1] > 0:
                for successor in self.precedence_graph[activity]['successors']:
                    if self.durations[successor-1] > 0:  # Ne pas ajouter d'arcs vers des activités fictives
                        dag.add_edge(activity, successor)
        
        # Trier les activités différemment de SPT et LPT
        # Utiliser un critère basé sur la durée et le nombre de successeurs
        if len(dag.nodes()) > 0:
            # Calculer le nombre de successeurs pour chaque activité
            num_successors = {node: len(list(dag.successors(node))) for node in dag.nodes()}
            
            # Calculer un score basé sur la durée et le nombre de successeurs
            # Score = durée * (1 + nombre de successeurs)
            scores = {node: self.durations[node-1] * (1 + num_successors[node]) for node in dag.nodes()}
            
            # Trier les activités par score décroissant
            sorted_activities = sorted([a for a in self.activities if self.durations[a-1] > 0], 
                                      key=lambda a: scores.get(a, 0), 
                                      reverse=True)
        else:
            # S'il n'y a pas de nœuds dans le graphe, trier simplement par durée
            sorted_activities = sorted([a for a in self.activities if self.durations[a-1] > 0],
                                      key=lambda a: self.durations[a-1],
                                      reverse=True)
        
        # Réordonner en respectant les contraintes de précédence
        ordered_activities = self._respect_precedence(sorted_activities)
        
        print(f"Activités ordonnées selon MST (approche alternative): {ordered_activities}")
        return ordered_activities
    
    def _respect_precedence(self, activities):
        """
        Réordonne les activités pour respecter les contraintes de précédence
        
        Args:
            activities (list): Liste des activités à réordonner
            
        Returns:
            list: Liste des activités réordonnées
        """
        # Créer un graphe orienté pour les précédences
        G = nx.DiGraph()
        
        # Ajouter les nœuds (activités)
        for activity in self.activities:
            G.add_node(activity)
        
        # Ajouter les arcs (précédences)
        for activity in self.activities:
            if activity in self.precedence_graph:  # Vérifier que l'activité est dans le graphe de précédence
                for successor in self.precedence_graph[activity]['successors']:
                    G.add_edge(activity, successor)
        
        # Calculer l'ordre topologique
        try:
            topological_order = list(nx.topological_sort(G))
            
            # Priorité des activités selon la liste originale 'activities'
            # Créer un dictionnaire avec les activités et leur priorité
            priority = {act: idx for idx, act in enumerate(activities)}
            
            # Tri les activités en respectant les précédences mais aussi en préservant
            # la priorité relative des activités venant de l'algorithme initial (SPT, LPT ou MST)
            result = []
            remaining = set(activities)
            
            # Pour chaque activité dans l'ordre topologique
            for act in topological_order:
                # Si cette activité est dans notre liste originale
                if act in remaining:
                    # Trouver toutes les activités prêtes (sans prédécesseurs non traités)
                    ready = set()
                    for a in remaining:
                        has_unprocessed_pred = False
                        if a in G:
                            for pred in G.predecessors(a):
                                if pred in remaining:
                                    has_unprocessed_pred = True
                                    break
                        if not has_unprocessed_pred:
                            ready.add(a)
                    
                    # Si des activités sont prêtes, choisir celle avec la meilleure priorité
                    if ready:
                        next_act = min(ready, key=lambda a: priority.get(a, float('inf')))
                        result.append(next_act)
                        remaining.remove(next_act)
            
            # S'il reste des activités (en cas de cycle), les ajouter dans l'ordre de priorité
            if remaining:
                print("Attention: cycle possible détecté, certaines activités ajoutées dans l'ordre de priorité")
                for act in sorted(remaining, key=lambda a: priority.get(a, float('inf'))):
                    result.append(act)
            
            return result
        except nx.NetworkXUnfeasible:
            print("Le graphe contient un cycle, impossible de respecter toutes les précédences")
            return activities  # Retourner l'ordre original en cas de cycle


def apply_algorithms_to_all_instances(instances_dir, results_dir):
    """
    Applique les algorithmes SPT, LPT et MST à toutes les instances
    
    Args:
        instances_dir (str): Chemin vers le répertoire des instances
        results_dir (str): Chemin vers le répertoire des résultats
    """
    # Créer les répertoires de résultats s'ils n'existent pas
    os.makedirs(os.path.join(results_dir, 'spt'), exist_ok=True)
    os.makedirs(os.path.join(results_dir, 'lpt'), exist_ok=True)
    os.makedirs(os.path.join(results_dir, 'mst'), exist_ok=True)
    
    # Parser toutes les instances
    instances = parse_all_instances(instances_dir)
    
    # Appliquer les algorithmes à chaque instance
    for instance_name, instance_data in instances.items():
        print(f"Traitement de l'instance {instance_name}...")
        
        # Initialiser les algorithmes
        algos = Algorithmes(instance_data)
        
        # Appliquer SPT
        spt_result = algos.spt()
        with open(os.path.join(results_dir, 'spt', f"{instance_name}.json"), 'w') as f:
            json.dump({
                'instance': instance_name,
                'algorithm': 'SPT',
                'ordered_activities': spt_result,
                'durations': [instance_data['dur'][a-1] for a in spt_result]
            }, f, indent=2)
        
        # Appliquer LPT
        lpt_result = algos.lpt()
        with open(os.path.join(results_dir, 'lpt', f"{instance_name}.json"), 'w') as f:
            json.dump({
                'instance': instance_name,
                'algorithm': 'LPT',
                'ordered_activities': lpt_result,
                'durations': [instance_data['dur'][a-1] for a in lpt_result]
            }, f, indent=2)
        
        # Appliquer MST
        mst_result = algos.mst()
        with open(os.path.join(results_dir, 'mst', f"{instance_name}.json"), 'w') as f:
            json.dump({
                'instance': instance_name,
                'algorithm': 'MST',
                'ordered_activities': mst_result,
                'durations': [instance_data['dur'][a-1] for a in mst_result]
            }, f, indent=2)
        
        print(f"Résultats pour {instance_name} enregistrés.")


if __name__ == "__main__":
    # Appliquer les algorithmes à toutes les instances
    instances_dir = "./projet_ordonnancement/instances"
    results_dir = "./projet_ordonnancement/resultats"
    
    apply_algorithms_to_all_instances(instances_dir, results_dir)