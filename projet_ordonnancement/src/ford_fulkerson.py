import os
import json
import networkx as nx
from collections import defaultdict
from parser_dzn import DznParser

def bfs_find_path(graph, source, sink):
    queue = [source]
    parents = {source: None}

    while queue:
        u = queue.pop(0)
        if u == sink:
            path = [sink]
            while path[-1] != source:
                path.append(parents[path[-1]])
            path.reverse()
            path_flow = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                path_flow = min(path_flow, graph[u][v])
            return path, path_flow
        for v in graph[u]:
            if v not in parents and graph[u][v] > 0:
                parents[v] = u
                queue.append(v)
    return None, 0

def ford_fulkerson(graph, source, sink):
    residual = defaultdict(dict)
    for u in graph:
        for v in graph[u]:
            residual[u][v] = graph[u][v]
            residual[v][u] = 0
    max_flow = 0
    while True:
        path, flow = bfs_find_path(residual, source, sink)
        if not path:
            break
        max_flow += flow
        u = source
        for v in path[1:]:
            residual[u][v] -= flow
            residual[v][u] += flow
            u = v
    return max_flow

def generate_ford_fulkerson_input(ordered_activities, instance_data):
    graph = defaultdict(dict)
    source = 's'
    sink = 't'
    durations = instance_data['dur']
    precedence_graph = instance_data['precedence_graph']

    print("🔎 Activités ordonnées :", ordered_activities)
    print("⏱️ Durées :", durations)

    for activity in ordered_activities:
        preds = precedence_graph.get(activity, {}).get('predecessors', [])
        dur = durations[activity - 1]
        if not preds or all(durations[p - 1] == 0 for p in preds):
            if dur > 0:
                graph[source][activity] = dur
            else:
                print(f"⚠️ Activité {activity} considérée source mais durée nulle.")

    for i in range(len(ordered_activities) - 1):
        current = ordered_activities[i]
        next_activity = ordered_activities[i + 1]
        if next_activity in precedence_graph.get(current, {}).get('successors', []):
            dur = durations[next_activity - 1]
            if dur > 0:
                graph[current][next_activity] = dur

    for activity in ordered_activities:
        succs = precedence_graph.get(activity, {}).get('successors', [])
        dur = durations[activity - 1]
        if not succs or all(durations[s - 1] == 0 for s in succs):
            if dur > 0:
                graph[activity][sink] = dur
            else:
                print(f"⚠️ Activité {activity} candidate pour le puits mais durée nulle.")

    if not graph[source]:
        print("❌ Aucun arc entre la source et les activités. Flot = 0 garanti.")
    if not any(sink in graph[node] for node in graph):
        print("❌ Aucun arc vers le puits. Flot = 0 garanti.")
    print("✅ Graphe généré :", dict(graph))
    return {'source': source, 'sink': sink, 'graph': graph}

def process_all_results(instances_dir, results_dir):
    os.makedirs(os.path.join(results_dir, 'ford_fulkerson'), exist_ok=True)
    for instance_file in os.listdir(instances_dir):
        if instance_file.endswith('.dzn'):
            instance_name = instance_file
            print(f"Traitement de l'instance {instance_name} pour Ford-Fulkerson...")
            parser = DznParser(os.path.join(instances_dir, instance_file))
            instance_data = parser.get_data()
            ff_results = {}

            for algo in ['spt', 'lpt', 'mst']:
                result_path = os.path.join(results_dir, algo, f"{instance_name}.json")
                if not os.path.exists(result_path):
                    print(f"⚠️ Fichier manquant : {result_path}")
                    continue
                with open(result_path, 'r') as f:
                    algo_result = json.load(f)
                    ordered_activities = algo_result['ordered_activities']
                    ff_input = generate_ford_fulkerson_input(ordered_activities, instance_data)
                    max_flow = ford_fulkerson(ff_input['graph'], ff_input['source'], ff_input['sink'])
                    ff_results[algo.upper()] = {
                        'max_flow': max_flow,
                        'ordered_activities': ordered_activities
                    }

            if not ff_results:
                print(f"❌ Aucun résultat de flot généré pour {instance_name}")
                continue

            priority = {'SPT': 3, 'LPT': 2, 'MST': 1}
            best_algo = max(ff_results.items(), key=lambda x: (x[1]['max_flow'], -priority[x[0]]))[0]

            with open(os.path.join(results_dir, 'ford_fulkerson', f"{instance_name}.json"), 'w') as f:
                json.dump({
                    'instance': instance_name,
                    'results': ff_results,
                    'best_algorithm': best_algo,
                    'best_max_flow': ff_results[best_algo]['max_flow']
                }, f, indent=2)

            print(f"✅ Meilleur algorithme: {best_algo} avec un flot maximal de {ff_results[best_algo]['max_flow']}")

if __name__ == "__main__":
    instances_dir = "./projet_ordonnancement/instances"
    results_dir = "./projet_ordonnancement/resultats"
    process_all_results(instances_dir, results_dir)
