# 🏭 OptiStock Solutions (Version 2.0 - FullStack)

> **Système IA et IoT d'Aide à la Décision (SAD) pour la Logistique d'Entrepôts.**

Projet réalisé dans le cadre du module **Apprentissage Par Projet**  
Filière : **Transformation Digitale Industrielle (TDI)**  
Université Sultan Moulay Slimane — ENSA Béni Mellal | Année 2025/2026  
Encadré par : **Pr. Hamza Touil**

---

## 👥 Équipe

| Nom | Rôle |
| :--- | :--- |
| **Rafiki Najat** | Ingénierie IoT & Data |
| **Atmane Salah** | Modélisation Mathématique |
| **ElAtraoui Haytame** | Architecture Full-Stack & UI/UX |

---

## 📌 Présentation
OptiStock Solutions est une plateforme logistique premium conçue pour les acteurs de la Supply Chain. Après une modernisation majeure, l'application est passée d'un prototype Streamlit à une solution **Full-Stack robuste** intégrant des algorithmes de recherche opérationnelle et un monitoring IoT temps réel.

### Points forts :
1. **Géolocalisation Prédictive** : Calcul du centre de gravité (Fermat-Weber) et recherche filtrée (Capteurs/IoT).
2. **Optimization Lab** : Expansion de réseau via Programmation Linéaire (MIP) et optimisation de tournées (VRP) avec Google OR-Tools.
3. **Monitoring IoT** : Surveillance thermique temps réel des unités de stockage.
4. **Interface Industrielle** : Design premium sous Next.js avec mode sombre et animations dynamiques.

---

## 🛠️ Stack Technique

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Frontend** | **Next.js 14 / React** | Interface réactive, Tailwind CSS, Framer Motion |
| **Backend** | **FastAPI (Python)** | Moteur de calcul, API REST, WebSocket IoT |
| **Optimisation** | **Google OR-Tools / Scipy** | Résolution MIP (Expansion) et VRP (Tournées) |
| **Base de données**| **SQLite** | Persistance des données et historique |
| **Cartographie** | **Leaflet (React-Leaflet)**| Visualisation géospatiale interactive |

---

## 📁 Structure du Projet

```text
optistock_solutions/
├── backend/                # Serveur FastAPI (Cœur algorithmique)
│   ├── core/               # Moteurs MIP, VRP, Weber et Routage
│   ├── routers/            # Endpoints API (Researcher, Owner, Admin)
│   ├── schemas/            # Validation Pydantic
│   └── database/           # Schémas et Données SQLite
│
├── frontend/               # Application Next.js (Interface utilisateur)
│   ├── src/app/            # Pages et Dashboard
│   ├── src/components/     # Composants UI, Cartes et Wizards
│   └── src/services/       # Appels API (Axios)
│
└── docs/                   # Documentation technique et audits
```

---

## 🚀 Installation & Lancement

### 1. Backend (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
python main.py
```
*Le serveur tourne sur `http://localhost:8000`*

### 2. Frontend (Node.js)
```bash
cd frontend
npm install
npm run dev
```
*L'application est accessible sur `http://localhost:3000`*

---

## 📝 Licence
Projet académique PFA — ENSA Béni Mellal © 2025/2026.  
Destiné à des fins de jury académique et d'audit.
