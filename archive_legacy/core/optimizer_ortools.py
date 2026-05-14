"""
core/optimizer_ortools.py — Résolution VRP (Ordre de Livraison)
================================================================
Détermine l'ordre optimal de visite des clients depuis un entrepôt.

Fallback automatique :
  1. OR-Tools (VRP exact)
  2. Nearest Neighbor TSP (heuristique, toujours disponible)
"""

import numpy as np

_ORTOOLS_OK = False
try:
    from ortools.constraint_solver import routing_enums_pb2, pywrapcp
    _ORTOOLS_OK = True
except ImportError:
    pass


def get_available_solver() -> str:
    return "OR-Tools (VRP)" if _ORTOOLS_OK else "Nearest Neighbor (TSP heuristique)"


class ORToolsLogisticOptimizer:
    """
    Calcule l'ordre optimal des livraisons (tournée depuis l'entrepôt).

    Entrées :
      warehouse_coord   : (lat, lon) de l'entrepôt dépôt
      clients_coords    : list de (lat, lon) des clients
      distance_matrix   : np.ndarray (n_nodes × n_nodes)
                          où node 0 = entrepôt, nodes 1..n = clients

    Retourne :
      {
        "status"         : "Success" | "Fail",
        "solver"         : str,
        "delivery_order" : list[int],   # indices clients dans clients_coords (0-based)
        "total_distance" : float,       # km ou unités de la matrice
        "route_labels"   : list[str],   # noms des étapes (si fournis)
      }
    """

    def __init__(self):
        self.last_solver = ""

    def compute_delivery_order(self, warehouse_coord, clients_coords,
                               distance_matrix, node_names=None):
        n_nodes = len(distance_matrix)

        if n_nodes <= 2:
            order = list(range(1, n_nodes))
            total = float(distance_matrix[0, order[0]]) if order else 0.0
            labels = self._build_labels(order, node_names)
            return {"status": "Success", "solver": "Trivial",
                    "delivery_order": order,
                    "total_distance": round(total, 2),
                    "route_labels": labels}

        if _ORTOOLS_OK:
            result = self._solve_ortools(distance_matrix)
            self.last_solver = "OR-Tools (VRP)"
        else:
            result = self._solve_nearest_neighbor(distance_matrix)
            self.last_solver = "Nearest Neighbor (TSP)"

        result["solver"] = self.last_solver
        result["route_labels"] = self._build_labels(
            result.get("delivery_order", []), node_names)
        return result

    # ── OR-Tools ──────────────────────────────────────────────────────────────
    def _solve_ortools(self, distance_matrix):
        try:
            n = len(distance_matrix)
            # Convertir en entiers (× 100 pour conserver 2 décimales)
            int_matrix = (np.array(distance_matrix) * 100).astype(int).tolist()

            manager = pywrapcp.RoutingIndexManager(n, 1, 0)
            routing = pywrapcp.RoutingModel(manager)

            def dist_cb(from_idx, to_idx):
                return int_matrix[manager.IndexToNode(from_idx)][
                    manager.IndexToNode(to_idx)]

            cb_idx = routing.RegisterTransitCallback(dist_cb)
            routing.SetArcCostEvaluatorOfAllVehicles(cb_idx)

            params = pywrapcp.DefaultRoutingSearchParameters()
            params.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
            params.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
            params.time_limit.seconds = 10

            solution = routing.SolveWithParameters(params)
            if solution:
                idx = routing.Start(0)
                order, total = [], 0
                while not routing.IsEnd(idx):
                    node = manager.IndexToNode(idx)
                    prev = idx
                    idx = solution.Value(routing.NextVar(idx))
                    total += routing.GetArcCostForVehicle(prev, idx, 0)
                    if node != 0:
                        order.append(node - 1)  # 0-based client index
                return {"status": "Success",
                        "delivery_order": order,
                        "total_distance": round(total / 100, 2)}
        except Exception:
            pass
        return self._solve_nearest_neighbor(distance_matrix)

    # ── Nearest Neighbor (fallback) ───────────────────────────────────────────
    def _solve_nearest_neighbor(self, distance_matrix):
        """
        Heuristique du plus proche voisin depuis le dépôt (node 0).
        Garantit toujours une solution valide.
        """
        n = len(distance_matrix)
        mat = np.array(distance_matrix, dtype=float)
        visited = [False] * n
        visited[0] = True
        route = [0]
        total = 0.0

        current = 0
        for _ in range(n - 1):
            row = mat[current].copy()
            row[visited] = np.inf  # masquer les nœuds visités
            if np.all(np.isinf(row)):
                break
            nxt = int(np.argmin(row))
            total += mat[current, nxt]
            visited[nxt] = True
            route.append(nxt)
            current = nxt

        # Retour au dépôt
        total += mat[current, 0]
        # Extraire les clients (tout sauf le dépôt 0)
        delivery_order = [node - 1 for node in route if node != 0]

        return {"status": "Success",
                "delivery_order": delivery_order,
                "total_distance": round(total, 2)}

    # ── Utilitaire labels ─────────────────────────────────────────────────────
    @staticmethod
    def _build_labels(delivery_order, node_names):
        if not node_names:
            return [f"Client {i + 1}" for i in delivery_order]
        labels = []
        for i in delivery_order:
            if 0 <= i < len(node_names):
                labels.append(node_names[i])
            else:
                labels.append(f"Client {i + 1}")
        return labels
