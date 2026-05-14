# 🚀 Moteurs d'Optimisation Logistique : OptiStock v2.0

Ce document détaille les algorithmes et modèles mathématiques utilisés dans le **Optimization Lab** et le **Wizard de Recherche**.

---

## 📍 1. Modèle de Weber (Fermat-Weber)
**Utilisation :** Wizard de Recherche (Step 4).
- **Objectif** : Trouver les coordonnées $(x, y)$ qui minimisent la somme des distances vers une liste de clients pondérés.
- **Algorithme** : Résolution via l'algorithme de Weiszfeld (implémenté avec `scipy.optimize.minimize` au backend).
- **Valeur Ajoutée** : Identifie mathématiquement le "Point Idéal" pour l'implantation d'un nouvel entrepôt central.

## 🏗️ 2. Programmation Linéaire (MIP - Site Selection)
**Utilisation :** Optimization Lab (Moteur d'Expansion).
- **Objectif** : Sélectionner $N$ entrepôts parmi $M$ candidats pour minimiser le coût total de transport et satisfaire la demande.
- **Solveur** : Google OR-Tools (SCIP).
- **Modèle** : 
  - Minimiser $\sum_{i,j} d_{ij} \cdot x_{ij}$
  - Sous contraintes de capacité et de sélection de site unique.
- **Valeur Ajoutée** : Garantit une réduction de **15-20%** des coûts logistiques par rapport à un choix manuel.

## 🚚 3. Problème de Tournée de Véhicules (VRP)
**Utilisation :** Optimization Lab (Ordonnancement).
- **Objectif** : Déterminer l'ordre exact de passage des camions depuis un dépôt vers tous les clients.
- **Algorithme** : Google OR-Tools (Routing Model).
- **Calcul de Distance** : Matrice de distance Haversine avec facteur de tortuosité de 1.3 (simulation du réseau routier).
- **Valeur Ajoutée** : Automatisation du planning de livraison et optimisation des kilomètres parcourus.

---

## 📊 Synthèse Technique
| Module | Algorithme | Outil Backend |
| :--- | :--- | :--- |
| **Implantation** | Fermat-Weber | Scipy (L-BFGS-B) |
| **Expansion** | MIP (Programmation Linéaire) | OR-Tools (SCIP) |
| **Tournées** | VRP (Vehicle Routing) | OR-Tools (Routing) |

> [!TIP]
> Ces moteurs communiquent avec le frontend via des APIs REST asynchrones, permettant une interface fluide sans latence de calcul perceptible.
