# 🚀 Mes Modifications à Réintégrer (Phase Optimisation Logistique)

> Ce fichier documente toutes les modifications que j'ai apportées au projet
> avant de faire `git stash` + `git pull` pour récupérer les améliorations de mes camarades.
> **Ces fichiers ont été supprimés temporairement pour éviter les erreurs de dépendances.**
> Une fois les améliorations des camarades intégrées, je peux recréer ces fichiers.

---

## 📁 Fichiers Créés (Untracked - à recréer)

### 1. `core/routing.py` — Moteur de Routage Géospatial (Dijkstra + GeoDataFrame)

**But :** Calcul des distances et temps de trajet réels sur un réseau routier via shapefile.

**Dépendances requises :**
```
geopandas
networkx
shapely
scipy
```

**Classes principales :**
- `RoadNetwork` : Charge un shapefile routier, construit un graphe NetworkX, expose `compute_shortest_path(lat1, lon1, lat2, lon2)`
- `OptiRouteOptimizer` : Wrapper qui calcule une matrice de distances entre sources et targets

**Code complet :**
```python
import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point, LineString
from scipy.spatial import cKDTree
import os
import warnings

warnings.filterwarnings("ignore")

class RoadNetwork:
    """
    Gestionnaire du réseau routier pour calcul de distances et temps de trajet réels.
    Utilise NetworkX pour trouver les plus courts chemins (Dijkstra).
    """
    
    def __init__(self, roads_shapefile, verbose=False):
        self.verbose = verbose
        self.graph = None
        self.nodes_gdf = None
        self.kdtree = None
        self._load_and_build_network(roads_shapefile)
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return 6371 * c
    
    def _load_and_build_network(self, shapefile_path):
        if not os.path.exists(shapefile_path):
            raise FileNotFoundError(f"Fichier routier introuvable : {shapefile_path}")
            
        gdf_roads = gpd.read_file(shapefile_path)
        if gdf_roads.crs is None:
            gdf_roads.set_crs("EPSG:4326", inplace=True)
        elif gdf_roads.crs.to_string() != "EPSG:4326":
            gdf_roads = gdf_roads.to_crs("EPSG:4326")
            
        self.graph = nx.Graph()
        node_id = 0
        node_coords = {}
        
        for idx, row in gdf_roads.iterrows():
            geom = row.geometry
            if not isinstance(geom, LineString): continue
            
            coords = list(geom.coords)
            road_type = row.get('type', 'regionale')
            speed_kmh = {'autoroute': 90, 'nationale': 70, 'regionale': 50, 'piste': 25}.get(road_type, 50)
            
            for i in range(len(coords) - 1):
                start, end = tuple(coords[i]), tuple(coords[i + 1])
                for pt in [start, end]:
                    if pt not in node_coords:
                        node_coords[pt] = node_id
                        self.graph.add_node(node_id, lon=pt[0], lat=pt[1])
                        node_id += 1
                
                length_km = self._haversine_distance(start[1], start[0], end[1], end[0])
                time_min = (length_km / speed_kmh) * 60
                self.graph.add_edge(node_coords[start], node_coords[end], 
                                    length=length_km, time=time_min, road_type=road_type)
        
        coords_array = np.array([[n['lon'], n['lat']] for n in self.graph.nodes(data=True)])
        self.kdtree = cKDTree(coords_array)

    def find_nearest_node(self, lat, lon):
        _, idx = self.kdtree.query([lon, lat])
        return idx

    def compute_shortest_path(self, s_lat, s_lon, t_lat, t_lon, weight='time'):
        s_node = self.find_nearest_node(s_lat, s_lon)
        t_node = self.find_nearest_node(t_lat, t_lon)
        
        if s_node == t_node:
            return {'distance_km': 0.0, 'time_min': 0.0, 'path': [s_node], 'accessible': True}
            
        try:
            path = nx.shortest_path(self.graph, source=s_node, target=t_node, weight=weight)
            total_l = sum(self.graph[path[i]][path[i+1]]['length'] for i in range(len(path)-1))
            total_t = sum(self.graph[path[i]][path[i+1]]['time'] for i in range(len(path)-1))
            return {'distance_km': total_l, 'time_min': total_t, 'path': path, 'accessible': True}
        except nx.NetworkXNoPath:
            return {'distance_km': np.inf, 'time_min': np.inf, 'path': None, 'accessible': False}

class OptiRouteOptimizer:
    """Intègre Dijkstra dans OptiStock pour les calculs de matrices."""
    
    def __init__(self, shapefile_path):
        self.network = RoadNetwork(shapefile_path)

    def get_matrix(self, sources, targets, weight='time'):
        """
        Calcule une matrice de coûts entre sources et targets.
        sources/targets: List de tuples (lat, lon)
        """
        matrix = np.zeros((len(sources), len(targets)))
        for i, s in enumerate(sources):
            for j, t in enumerate(targets):
                res = self.network.compute_shortest_path(s[0], s[1], t[0], t[1], weight=weight)
                matrix[i, j] = res['distance_km'] if weight == 'length' else res['time_min']
        return matrix
```

---

### 2. `core/optimizer_gurobi.py` — Optimisation d'expansion (Gurobi ILP)

**But :** Modèle de Programme Linéaire en Nombres Entiers (PLNE) pour choisir les meilleurs nouveaux emplacements d'entrepôts.

**Dépendances requises :**
```
gurobipy  (+ licence Gurobi académique)
```

**Classe principale :** `GurobiExpansionOptimizer`
- Méthode `optimize_expansion(existing_warehouses, candidate_sites, clients, cost_matrix, n_to_add=1)`
- Variables binaires : `x[i]` = activer candidat i, `y[i,j]` = assigner client j à entrepôt i
- Objectif : Minimiser la somme des distances pondérées par la demande
- Contraintes : Exactement `n_to_add` candidats, chaque client assigné une fois, capacités respectées

**Code complet :**
```python
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pandas as pd

class GurobiExpansionOptimizer:
    def __init__(self):
        self.model = None

    def optimize_expansion(self, existing_warehouses, candidate_sites, clients, 
                           cost_matrix, n_to_add=1):
        n_existing = len(existing_warehouses)
        n_candidates = len(candidate_sites)
        n_clients = len(clients)
        n_total = n_existing + n_candidates
        
        self.model = gp.Model("optistock_expansion")
        self.model.setParam('OutputFlag', 0)
        
        x = self.model.addVars(n_candidates, vtype=GRB.BINARY, name="activate_candidate")
        y = self.model.addVars(n_total, n_clients, vtype=GRB.BINARY, name="assign")
        
        obj = 0
        for i in range(n_total):
            for j in range(n_clients):
                demand = clients[j].get('demand', 1)
                obj += cost_matrix[i, j] * demand * y[i, j]
        self.model.setObjective(obj, GRB.MINIMIZE)
        
        self.model.addConstr(gp.quicksum(x[i] for i in range(n_candidates)) == n_to_add)
        for j in range(n_clients):
            self.model.addConstr(gp.quicksum(y[i, j] for i in range(n_total)) == 1)
        for i in range(n_candidates):
            for j in range(n_clients):
                self.model.addConstr(y[n_existing + i, j] <= x[i])
        for i in range(n_total):
            total_warehouses = existing_warehouses + candidate_sites
            capacity = total_warehouses[i].get('capacity', 1e9)
            self.model.addConstr(gp.quicksum(clients[j].get('demand', 1) * y[i, j] for j in range(n_clients)) <= capacity)
            
        self.model.optimize()
        
        if self.model.Status == GRB.OPTIMAL:
            selected_candidates = [i for i in range(n_candidates) if x[i].X > 0.5]
            assignments = {}
            for i in range(n_total):
                assigned_clients = [j for j in range(n_clients) if y[i, j].X > 0.5]
                assignments[i] = assigned_clients
            return {
                "status": "Optimal",
                "selected_candidate_indices": selected_candidates,
                "objective_value": self.model.ObjVal,
                "assignments": assignments
            }
        else:
            return {"status": "Infeasible/Other", "obj": None}
```

---

### 3. `core/optimizer_ortools.py` — Optimisation VRP (OR-Tools)

**But :** Résolution du Problème de Tournée de Véhicules (VRP) pour l'ordre optimal de livraison.

**Dépendances requises :**
```
ortools
```

**Classe principale :** `ORToolsLogisticOptimizer`
- Méthode `compute_delivery_order(warehouse_coord, clients_coords, distance_matrix)`
- Utilise `PATH_CHEAPEST_ARC` comme stratégie initiale
- Retourne l'ordre des clients à visiter + distance totale

**Code complet :**
```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np

class ORToolsLogisticOptimizer:
    def __init__(self):
        pass

    def compute_delivery_order(self, warehouse_coord, clients_coords, distance_matrix):
        data = {}
        data['distance_matrix'] = distance_matrix
        data['num_vehicles'] = 1
        data['depot'] = 0
        
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_vehicles'], data['depot'])
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(data['distance_matrix'][from_node][to_node] * 100)

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            index = routing.Start(0)
            plan_output = []
            route_distance = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                plan_output.append(node_index)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            order = plan_output[1:]
            return {"status": "Success", "delivery_order": order, "total_distance": route_distance / 100.0}
        else:
            return {"status": "Fail"}
```

---

### 4. Pages Streamlit créées

- `pages/4_🚀_Optimization_Lab.py` — Page principale de l'Optimization Lab (importait les 3 moteurs ci-dessus)
- `pages/optimization_lab_view.py` — Vue alternative du lab d'optimisation

> ⚠️ Ces pages importaient `core.routing`, `core.optimizer_gurobi`, `core.optimizer_ortools`.
> À recréer après installation des dépendances ou en adaptant pour éviter geopandas si pas disponible.

### 5. Autres fichiers

- `data/gis/` — Dossier contenant les shapefiles du réseau routier marocain
- `PRESENTATION_TECHNIQUE_OPTIMISATION.md` — Présentation technique de l'approche d'optimisation

---

## 📦 Dépendances à installer pour réintégrer

```bash
pip install geopandas networkx shapely scipy
pip install ortools
# Gurobi nécessite une licence académique : https://www.gurobi.com/academia/academic-program-and-licenses/
pip install gurobipy
```

## 🔁 Étapes pour réintégrer

1. Installer les dépendances ci-dessus
2. Recréer `core/routing.py` avec le code documenté ici
3. Recréer `core/optimizer_gurobi.py` avec le code documenté ici
4. Recréer `core/optimizer_ortools.py` avec le code documenté ici
5. Recréer les pages Streamlit
6. Tester avec `streamlit run app.py`
