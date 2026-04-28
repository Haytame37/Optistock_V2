"""
core/optimizer_mip.py — Optimisation d'Expansion Logistique (MIP)
========================================================================
Sélectionne les meilleurs sites candidats pour de nouveaux entrepôts
en minimisant le coût total de transport pondéré par la demande client.

Utilise Google OR-Tools (solveur SCIP) comme alternative 100% gratuite 
et open-source à Gurobi. Fallback sur une Heuristique Greedy si OR-Tools
n'est pas disponible.
"""

import numpy as np
from itertools import combinations

_ORTOOLS_OK = False
try:
    from ortools.linear_solver import pywraplp
    _ORTOOLS_OK = True
except ImportError:
    pass

def get_available_solver() -> str:
    return "OR-Tools (SCIP Optimal)" if _ORTOOLS_OK else "Heuristique Greedy"

class MipExpansionOptimizer:
    def __init__(self):
        self.last_solver = ""

    def optimize_expansion(self, existing_warehouses, candidate_sites,
                           clients, cost_matrix, n_to_add=1):
        n_existing   = len(existing_warehouses)
        n_candidates = len(candidate_sites)
        n_clients    = len(clients)

        if n_candidates == 0:
            return {"status": "Error", "solver": "N/A",
                    "selected_candidate_indices": [],
                    "selected_candidate_names": [],
                    "objective_value": 0.0,
                    "assignments": {}, "savings_vs_random": 0.0}

        n_to_add = min(n_to_add, n_candidates)
        random_obj = self._random_baseline(
            n_existing, n_candidates, n_clients, clients, cost_matrix, n_to_add)

        if _ORTOOLS_OK:
            result = self._solve_ortools_mip(
                n_existing, n_candidates, n_clients, clients, cost_matrix, n_to_add)
            self.last_solver = "OR-Tools (SCIP Optimal)"
        else:
            result = self._solve_greedy(
                n_existing, n_candidates, n_clients, clients, cost_matrix, n_to_add)
            self.last_solver = "Heuristique Greedy"

        result["solver"] = self.last_solver
        result["selected_candidate_names"] = [
            candidate_sites[i]["name"]
            for i in result.get("selected_candidate_indices", [])
            if i < n_candidates
        ]
        savings = 0.0
        if random_obj and random_obj > 0:
            obj = result.get("objective_value", random_obj)
            savings = round((random_obj - obj) / random_obj * 100, 1)
        result["savings_vs_random"] = savings
        return result

    def _solve_ortools_mip(self, n_existing, n_candidates, n_clients,
                           clients, cost_matrix, n_to_add):
        try:
            solver = pywraplp.Solver.CreateSolver('SCIP')
            if not solver:
                raise Exception("SCIP solver not available")
            
            n_total = n_existing + n_candidates
            
            # x[i] = 1 si le candidat i est sélectionné
            x = {}
            for i in range(n_candidates):
                x[i] = solver.IntVar(0, 1, f'x_{i}')
                
            # y[i, j] = 1 si le client j est assigné au site i (existant ou candidat)
            y = {}
            for i in range(n_total):
                for j in range(n_clients):
                    y[i, j] = solver.IntVar(0, 1, f'y_{i}_{j}')
                    
            # Objectif : minimiser le coût total pondéré
            demands = [clients[j].get("demand", 1) for j in range(n_clients)]
            objective = solver.Objective()
            for i in range(n_total):
                for j in range(n_clients):
                    objective.SetCoefficient(y[i, j], float(cost_matrix[i, j] * demands[j]))
            objective.SetMinimization()
            
            # Contrainte 1 : on sélectionne exactement n_to_add candidats
            solver.Add(sum(x[i] for i in range(n_candidates)) == n_to_add)
            
            # Contrainte 2 : chaque client est assigné à exactement un site
            for j in range(n_clients):
                solver.Add(sum(y[i, j] for i in range(n_total)) == 1)
                
            # Contrainte 3 : on ne peut assigner un client à un candidat que si ce candidat est sélectionné
            for i in range(n_candidates):
                for j in range(n_clients):
                    solver.Add(y[n_existing + i, j] <= x[i])
                    
            status = solver.Solve()
            
            if status == pywraplp.Solver.OPTIMAL:
                selected = [i for i in range(n_candidates) if x[i].solution_value() > 0.5]
                assignments = {
                    i: [j for j in range(n_clients) if y[i, j].solution_value() > 0.5]
                    for i in range(n_total)
                }
                return {"status": "Optimal",
                        "selected_candidate_indices": selected,
                        "objective_value": round(objective.Value(), 2),
                        "assignments": assignments}
        except Exception as e:
            print(f"OR-Tools MIP fallback because: {e}")
            pass
            
        return self._solve_greedy(
            n_existing, n_candidates, n_clients, clients, cost_matrix, n_to_add)

    def _solve_greedy(self, n_existing, n_candidates, n_clients,
                      clients, cost_matrix, n_to_add):
        demands = np.array([c.get("demand", 1) for c in clients])
        best_obj = np.inf
        best_sel = list(range(min(n_to_add, n_candidates)))

        for combo in combinations(range(n_candidates), n_to_add):
            active = list(range(n_existing)) + [n_existing + i for i in combo]
            sub = cost_matrix[active, :]
            obj = float((sub.min(axis=0) * demands).sum())
            if obj < best_obj:
                best_obj = obj
                best_sel = list(combo)

        n_total = n_existing + n_candidates
        active_f = list(range(n_existing)) + [n_existing + i for i in best_sel]
        sub_f = cost_matrix[active_f, :]
        best_local = sub_f.argmin(axis=0)
        assignments = {i: [] for i in range(n_total)}
        for j, li in enumerate(best_local):
            assignments[active_f[li]].append(j)

        return {"status": "Heuristic",
                "selected_candidate_indices": best_sel,
                "objective_value": round(best_obj, 2),
                "assignments": assignments}

    def _random_baseline(self, n_existing, n_candidates, n_clients,
                         clients, cost_matrix, n_to_add):
        demands = np.array([c.get("demand", 1) for c in clients])
        rng = np.random.default_rng(0)
        sel = rng.choice(n_candidates, size=n_to_add, replace=False).tolist()
        active = list(range(n_existing)) + [n_existing + i for i in sel]
        sub = cost_matrix[active, :]
        return float((sub.min(axis=0) * demands).sum())
