"""
core/routing.py — Moteur de Routage Géospatial
===============================================
Calcul des distances et temps de trajet réels via un réseau routier (Shapefile).
Utilise NetworkX + KDTree pour Dijkstra.

Fallback automatique vers Haversine si geopandas / networkx / scipy sont absents.
"""

import numpy as np
import warnings

warnings.filterwarnings("ignore")

# ── Détection des dépendances optionnelles ────────────────────────────────────
_GEOPANDAS_OK = False
_NETWORKX_OK  = False
_SCIPY_OK     = False

try:
    import geopandas as gpd
    from shapely.geometry import LineString
    _GEOPANDAS_OK = True
except ImportError:
    pass

try:
    import networkx as nx
    _NETWORKX_OK = True
except ImportError:
    pass

try:
    from scipy.spatial import cKDTree
    _SCIPY_OK = True
except ImportError:
    pass

ROUTING_ADVANCED = _GEOPANDAS_OK and _NETWORKX_OK and _SCIPY_OK


# ── Haversine utilitaire ──────────────────────────────────────────────────────
def _haversine(lat1, lon1, lat2, lon2) -> float:
    """Distance Haversine en km entre deux points GPS."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


# ── Classe principale ─────────────────────────────────────────────────────────
class RoadNetwork:
    """
    Gestionnaire du réseau routier pour calcul de distances et temps de trajet réels.
    Utilise NetworkX (Dijkstra) + KDTree pour la recherche du nœud le plus proche.

    Si les dépendances sont absentes → mode Haversine avec facteur de tortuosité 1.3.
    """

    SPEED_MAP = {
        "autoroute": 120,
        "nationale":  80,
        "regionale":  60,
        "piste":      30,
    }
    TORTUOSITY = 1.3  # Facteur de correction Haversine → distance réelle

    def __init__(self, roads_shapefile: str = None, verbose: bool = False):
        self.verbose = verbose
        self.graph = None
        self.kdtree = None
        self._node_coords = None
        self._mode = "haversine"

        if roads_shapefile and ROUTING_ADVANCED:
            try:
                self._load_and_build_network(roads_shapefile)
                self._mode = "dijkstra"
                if verbose:
                    print(f"[RoadNetwork] Réseau chargé — {self.graph.number_of_nodes()} nœuds, "
                          f"{self.graph.number_of_edges()} arcs")
            except Exception as exc:
                if verbose:
                    print(f"[RoadNetwork] Impossible de charger le shapefile ({exc}). Fallback Haversine.")
        else:
            if verbose:
                reason = "shapefile non fourni" if not roads_shapefile else "dépendances manquantes"
                print(f"[RoadNetwork] Mode Haversine ({reason})")

    # ── Chargement du shapefile ───────────────────────────────────────────────
    def _load_and_build_network(self, shapefile_path: str):
        import os
        if not os.path.exists(shapefile_path):
            raise FileNotFoundError(f"Shapefile introuvable : {shapefile_path}")

        gdf = gpd.read_file(shapefile_path)
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        elif gdf.crs.to_string() != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")

        G = nx.Graph()
        node_id = 0
        coord_to_id: dict = {}

        for _, row in gdf.iterrows():
            geom = row.geometry
            if not isinstance(geom, LineString):
                continue

            road_type = str(row.get("type", "regionale")).lower()
            speed = self.SPEED_MAP.get(road_type, 60)

            coords = list(geom.coords)
            for i in range(len(coords) - 1):
                p0, p1 = tuple(coords[i]), tuple(coords[i + 1])
                for pt in (p0, p1):
                    if pt not in coord_to_id:
                        coord_to_id[pt] = node_id
                        G.add_node(node_id, lon=pt[0], lat=pt[1])
                        node_id += 1

                dist_km  = _haversine(p0[1], p0[0], p1[1], p1[0])
                time_min = (dist_km / speed) * 60
                G.add_edge(coord_to_id[p0], coord_to_id[p1],
                           length=dist_km, time=time_min, road_type=road_type)

        self.graph = G
        arr = np.array([[d["lon"], d["lat"]] for _, d in G.nodes(data=True)])
        self._node_coords = arr
        self.kdtree = cKDTree(arr)

    # ── Recherche du nœud le plus proche ─────────────────────────────────────
    def find_nearest_node(self, lat: float, lon: float) -> int:
        _, idx = self.kdtree.query([lon, lat])
        return int(idx)

    # ── Calcul du plus court chemin ───────────────────────────────────────────
    def compute_shortest_path(
        self, s_lat: float, s_lon: float, t_lat: float, t_lon: float, weight: str = "time"
    ) -> dict:
        """
        Retourne un dict :
          distance_km, time_min, path (list de node ids ou None), accessible (bool), mode
        """
        if self._mode == "dijkstra":
            return self._dijkstra(s_lat, s_lon, t_lat, t_lon, weight)
        return self._haversine_path(s_lat, s_lon, t_lat, t_lon)

    def _dijkstra(self, s_lat, s_lon, t_lat, t_lon, weight) -> dict:
        s_node = self.find_nearest_node(s_lat, s_lon)
        t_node = self.find_nearest_node(t_lat, t_lon)

        if s_node == t_node:
            return {"distance_km": 0.0, "time_min": 0.0, "path": [s_node],
                    "accessible": True, "mode": "dijkstra"}
        try:
            path = nx.shortest_path(self.graph, s_node, t_node, weight=weight)
            dist = sum(self.graph[path[i]][path[i + 1]]["length"] for i in range(len(path) - 1))
            time = sum(self.graph[path[i]][path[i + 1]]["time"]   for i in range(len(path) - 1))
            return {"distance_km": round(dist, 2), "time_min": round(time, 1),
                    "path": path, "accessible": True, "mode": "dijkstra"}
        except nx.NetworkXNoPath:
            return self._haversine_path(s_lat, s_lon, t_lat, t_lon)

    def _haversine_path(self, s_lat, s_lon, t_lat, t_lon) -> dict:
        dist = _haversine(s_lat, s_lon, t_lat, t_lon) * self.TORTUOSITY
        time = (dist / 80) * 60  # vitesse moyenne 80 km/h
        return {"distance_km": round(dist, 2), "time_min": round(time, 1),
                "path": None, "accessible": True, "mode": "haversine"}

    @property
    def mode(self) -> str:
        return self._mode


# ── Classe Wrapper ────────────────────────────────────────────────────────────
class OptiRouteOptimizer:
    """
    Intègre le moteur de routage dans OptiStock pour les calculs de matrices.
    Expose get_matrix(sources, targets) pour alimenter Gurobi / OR-Tools.
    """

    def __init__(self, shapefile_path: str = None):
        self.network = RoadNetwork(shapefile_path)

    def get_matrix(self, sources: list, targets: list, weight: str = "time") -> np.ndarray:
        """
        sources / targets : liste de tuples (lat, lon)
        Retourne une matrice numpy (n_sources × n_targets) en minutes (weight='time')
        ou en km (weight='length').
        """
        matrix = np.zeros((len(sources), len(targets)))
        for i, (s_lat, s_lon) in enumerate(sources):
            for j, (t_lat, t_lon) in enumerate(targets):
                res = self.network.compute_shortest_path(s_lat, s_lon, t_lat, t_lon, weight)
                matrix[i, j] = res["distance_km"] if weight == "length" else res["time_min"]
        return matrix

    @property
    def mode(self) -> str:
        return self.network.mode
