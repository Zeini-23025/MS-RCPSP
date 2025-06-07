#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour parser les fichiers .dzn et extraire les données pertinentes
"""

import re
import os
import glob

class DznParser:
    """
    Classe pour parser les fichiers .dzn et extraire les données
    """
    def __init__(self, file_path):
        """
        Initialise le parser avec le chemin du fichier .dzn
        
        Args:
            file_path (str): Chemin vers le fichier .dzn
        """
        self.file_path = file_path
        self.data = {}
        self._parse_file()
    
    def _parse_file(self):
        """
        Parse le fichier .dzn et extrait les données
        """
        with open(self.file_path, 'r') as f:
            content = f.read()
        
        # Extraire les valeurs principales
        self.data['mint'] = self._extract_int_value(content, r'mint\s*=\s*(\d+)')
        self.data['nActs'] = self._extract_int_value(content, r'nActs\s*=\s*(\d+)')
        
        # Extraire les durées des activités
        dur_match = re.search(r'dur\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if dur_match:
            dur_str = dur_match.group(1).strip()
            self.data['dur'] = [int(d) for d in dur_str.split(',')]
        
        # Extraire les précédences
        pred_match = re.search(r'pred\s*=\s*\[(.*?)\]', content, re.DOTALL)
        succ_match = re.search(r'succ\s*=\s*\[(.*?)\]', content, re.DOTALL)
        
        if pred_match and succ_match:
            pred_str = pred_match.group(1).strip()
            succ_str = succ_match.group(1).strip()
            
            self.data['pred'] = [int(p) for p in pred_str.split(',')]
            self.data['succ'] = [int(s) for s in succ_str.split(',')]
            
            # Créer un graphe de précédence
            self.data['precedence_graph'] = self._create_precedence_graph()
        
        # Extraire les compétences requises
        sreq_match = re.search(r'sreq\s*=\s*\[\|(.*?)\|\]', content, re.DOTALL)
        if sreq_match:
            sreq_str = sreq_match.group(1).strip()
            sreq_lines = [line.strip() for line in sreq_str.split('\n')]
            sreq_matrix = []
            
            for line in sreq_lines:
                # Nettoyer la ligne des caractères non désirés
                line = line.replace('|', '').strip()
                if ',' in line:
                    # Gérer les valeurs vides
                    skills = []
                    for s in line.split(','):
                        s = s.strip()
                        if s and s.isdigit():  # Vérifier que la chaîne n'est pas vide et est un nombre
                            skills.append(int(s))
                        else:
                            skills.append(0)  # Valeur par défaut pour les chaînes vides ou non numériques
                    
                    if skills:  # S'assurer que la liste n'est pas vide
                        sreq_matrix.append(skills)
            
            self.data['sreq'] = sreq_matrix
        
        # Extraire les ressources
        self.data['nResources'] = self._extract_int_value(content, r'nResources\s*=\s*(\d+)')
        
        # Extraire les maîtrises
        mastery_match = re.search(r'mastery\s*=\s*\[\|(.*?)\|\]', content, re.DOTALL)
        if mastery_match:
            mastery_str = mastery_match.group(1).strip()
            mastery_lines = [line.strip() for line in mastery_str.split('\n')]
            mastery_matrix = []
            
            for line in mastery_lines:
                # Nettoyer la ligne des caractères non désirés
                line = line.replace('|', '').strip()
                if ',' in line:
                    # Gérer les valeurs vides
                    skills = []
                    for s in line.split(','):
                        s = s.strip()
                        if s:  # Vérifier que la chaîne n'est pas vide
                            skills.append(s == 'true')
                        else:
                            skills.append(False)  # Valeur par défaut pour les chaînes vides
                    
                    if skills:  # S'assurer que la liste n'est pas vide
                        mastery_matrix.append(skills)
            
            self.data['mastery'] = mastery_matrix
    
    def _extract_int_value(self, content, pattern):
        """
        Extrait une valeur entière à partir d'un motif regex
        
        Args:
            content (str): Contenu du fichier
            pattern (str): Motif regex pour extraire la valeur
            
        Returns:
            int: Valeur extraite ou None si non trouvée
        """
        match = re.search(pattern, content)
        if match:
            return int(match.group(1))
        return None
    
    def _create_precedence_graph(self):
        """
        Crée un graphe de précédence à partir des listes pred et succ
        
        Returns:
            dict: Graphe de précédence sous forme de dictionnaire
        """
        graph = {}
        n_acts = self.data['nActs']
        
        # Initialiser le graphe
        for i in range(1, n_acts + 1):
            graph[i] = {'successors': [], 'predecessors': []}
        
        # Ajouter les arcs
        for p, s in zip(self.data['pred'], self.data['succ']):
            graph[p]['successors'].append(s)
            graph[s]['predecessors'].append(p)
        
        return graph
    
    def get_data(self):
        """
        Retourne les données extraites
        
        Returns:
            dict: Données extraites du fichier .dzn
        """
        return self.data


def parse_all_instances(instances_dir):
    """
    Parse tous les fichiers .dzn dans le répertoire spécifié
    
    Args:
        instances_dir (str): Chemin vers le répertoire contenant les fichiers .dzn
        
    Returns:
        dict: Dictionnaire des instances parsées (clé: nom du fichier, valeur: données)
    """
    instances = {}
    
    # Trouver tous les fichiers .dzn
    dzn_files = glob.glob(os.path.join(instances_dir, '*.dzn'))
    
    for file_path in dzn_files:
        file_name = os.path.basename(file_path)
        parser = DznParser(file_path)
        instances[file_name] = parser.get_data()
    
    return instances


if __name__ == "__main__":
    # Test du parser sur un exemple
    parser = DznParser("/home/ubuntu/projet_ordonnancement/instances/exemple.dzn")
    data = parser.get_data()
    
    print(f"Nombre d'activités: {data['nActs']}")
    print(f"Durées des activités: {data['dur']}")
    print(f"Graphe de précédence: {data['precedence_graph']}")
