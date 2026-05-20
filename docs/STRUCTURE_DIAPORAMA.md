# 🖼️ Conception des Diapositives : Structure et Contenu Visuel (PFE OptiStock)

Ce document décrit en détail le contenu textuel et les suggestions visuelles pour concevoir votre support de présentation (sur PowerPoint, Canva, Marp ou via Claude). Il adopte un **thème épuré, professionnel et moderne**, évitant la surcharge de texte au profit de la clarté.

---

### 🎨 Thème Visuel Recommandé : "Sleek Industrial & Tech"
*   **Palette de couleurs** : Blanc/Gris très clair (arrière-plan principal), Bleu Nuit (couleur primaire pour les titres et la structure), Vert Émeraude ou Cyan (couleur d'accentuation pour souligner les réussites, l'IoT et les validations).
*   **Typographie** : Sans-serif moderne (ex: *Inter*, *Montserrat* ou *Roboto*) pour un rendu technologique et lisible.
*   **Règle d'or** : Jamais plus de 4 puces de texte par diapositive. Utilisez des icônes et des flèches directionnelles pour matérialiser les flux.

---

## 🖥️ Diapositive 1 : Page de Garde
*   **Rôle** : Accueil du jury et présentation générale.
*   **Titre Principal** : OPTISTOCK
*   **Sous-titre** : Plateforme Intégrée de Gestion Logistique, Monitoring IoT et Intelligence Artificielle
*   **Contenu Textuel** :
    *   *Présenté par* : [Votre Nom]
    *   *Projet de Fin d'Études* pour l'obtention du Diplôme d'Ingénieur d'État
    *   *Encadrants* : [Nom de vos encadrants académiques & professionnels]
    *   *Année Universitaire* : 2025 - 2026
*   **Visuels** : Logos officiels (Établissement & Entreprise d'accueil) placés en haut ou en bas. Une capture d'écran épurée de l'interface en arrière-plan avec une opacité de 15%.

---

## 🖥️ Diapositive 2 : Sommaire (Agenda)
*   **Rôle** : Donner une vue d'ensemble claire du déroulement logique.
*   **Titre** : Sommaire de la Présentation
*   **Contenu Textuel (Puces structurées)** :
    *   **01 | Le Défi Métier** : Contexte & Problématique Logistique
    *   **02 | La Vision Produit** : Qu'est-ce qu'OptiStock ?
    *   **03 | Les Chaînes de Valeur** : Fonctionnement complet des 3 modules clés
    *   **04 | L'Architecture & Les Choix Techniques** : Notre infrastructure robuste
    *   **05 | Démonstration en Direct** : L'application sur site en action
    *   **06 | Qualité & Perspectives** : Bilan de l'audit technique et horizons futurs
*   **Visuels** : Une ligne temporelle ou un indicateur de progression à gauche pour guider le regard du jury.

---

## 🖥️ Diapositive 3 : Le Contexte et la Problématique
*   **Rôle** : Capturer l'attention en démontrant le besoin économique réel.
*   **Titre** : Le Défi Logistique
*   **Contenu Textuel (Les 3 Douleurs Métier)** :
    *   🛑 **Opacité du Stockage** : Difficulté de mise en relation rapide et transparente entre offreurs (propriétaires) et demandeurs d'entrepôts.
    *   🌡️ **Rupture de la Chaîne du Froid** : Manque de suivi rigoureux et en temps réel de la conformité thermique des stocks (perte de marchandises sensibles).
    *   🚛 **Coût du Dernier Kilomètre** : Absence d'outils d'optimisation mathématique pour minimiser les distances et réduire les coûts de transport.
*   **Visuels** : 3 blocs horizontaux ou icônes de couleur contrastée (Rouge/Orange) pour symboliser les problèmes majeurs du marché marocain.

---

## 🖥️ Diapositive 4 : La Solution OptiStock
*   **Rôle** : Révéler le produit et sa vision unifiée.
*   **Titre** : La Solution : Un Écosystème Connecté Unique
*   **Contenu Textuel** :
    *   🤝 **Marketplace Tripartite** : Un espace de confiance qui interconnecte Administrateurs, Propriétaires et Chercheurs.
    *   📡 **Sentinel IoT** : Monitoring continu de la température et de l'humidité avec alertes automatiques instantanées.
    *   🧠 **Optimization Lab & IA** : Algorithmes de recherche opérationnelle combinés à un agent d'IA conversationnelle contextuel.
*   **Visuels** : Un schéma circulaire au centre montrant l'interconnexion des 3 piliers (Marketplace, IoT, IA/Mathématiques).

---

## 🖥️ Diapositive 5 : Chaîne de Valeur n°1 – Sentinel IoT (Pipeline Complet)
*   **Rôle** : Expliquer comment la donnée IoT circule de bout en bout de façon claire.
*   **Titre** : Chaîne IoT : De la Mesure à l'Alerte d'Urgence
*   **Contenu Textuel (Les Étapes du Data Flow)** :
    1.  **Mesure** : Les capteurs (Proteus/ESP32) mesurent la température et l'humidité.
    2.  **Ingestion** : La télémétrie est transmise de manière sécurisée à la gateway **ThingsBoard**.
    3.  **Relais & Rendu** : Le back-end FastAPI proxyfie les séries temporelles affichées en direct sur les graphiques Next.js.
    4.  **Alerte Sentinel** : Déclenchement automatique d'un protocole d'alerte SMTP (email d'urgence) en cas de dépassement de seuil.
*   **Visuels** : Un diagramme linéaire horizontal avec des flèches (Capteurs ➔ ThingsBoard ➔ FastAPI ➔ Next.js + SMTP) avec des icônes d'appareils et de réseau.

---

## 🖥️ Diapositive 6 : Chaîne de Valeur n°2 – L'Optimization Lab
*   **Rôle** : Expliquer le moteur d'aide à la décision logistique.
*   **Titre** : Chaîne Mathématique : Aide à la Décision Logistique
*   **Contenu Textuel** :
    *   🎯 **Objectif** : Trouver l'entrepôt logistique optimal en minimisant les coûts et la distance.
    *   📈 **Algorithme Multicritères (Weighted Decision Score)** :
        *   **40 % Distance** : Calcul géodésique précis via la **formule Haversine**.
        *   **30 % Rentabilité** : Ratio prix/surface.
        *   **30 % Fiabilité IoT** : Stabilité historique des capteurs environnementaux.
    *   🧮 **Moteur Linéaire** : Résolution par programmation en nombres entiers (MIP/OR-Tools).
*   **Visuels** : Affichage clair de la formule mathématique du Score pondéré dans un encadré stylisé.

---

## 🖥️ Diapositive 7 : Chaîne de Valeur n°3 – L'Assistance IA Contextuelle
*   **Rôle** : Démontrer l'intégration moderne de l'IA (OptiBot).
*   **Titre** : Chaîne IA : OptiBot, le Copilote Logistique
*   **Contenu Textuel** :
    *   🤖 **Moteur d'IA** : Intégration de l'API de pointe **Google Gemini Pro**.
    *   👥 **Conscience de Rôle (Role-aware Prompts)** : L'IA identifie instantanément le rôle de l'utilisateur connecté :
        *   *Mode Propriétaire* : Conseils de maintenance thermique, conformité des capteurs, optimisation d'espace.
        *   *Mode Chercheur* : Critères de conservation des denrées, aide à la négociation, recommandations logistiques.
*   **Visuels** : Deux bulles de chat contrastées illustrant une réponse d'un côté pour un Propriétaire et de l'autre pour un Chercheur.

---

## 🖥️ Diapositive 8 : Architecture Technique & Choix Technologiques
*   **Rôle** : Présenter la pile logicielle et prouver sa pertinence face au jury.
*   **Titre** : Choix Technologiques & Architecture Découplée
*   **Contenu Textuel** :
    *   💻 **Frontend (Next.js 14 / React)** : Composants serveur sécurisés, animations fluides (Framer Motion), réactivité optimale.
    *   ⚡ **Backend (FastAPI / Python)** : Execution asynchrone (ASGI) ultra-rapide, idéal pour l'ingestion IoT et le relais d'API.
    *   📡 **IoT Gateway (ThingsBoard)** : Serveur dédié à la gestion sécurisée des équipements et à l'historisation des capteurs.
    *   💾 **Persistance (SQLite)** : Base de données relationnelle portable assurant l'intégrité SQL et la simplicité de déploiement du prototype.
*   **Visuels** : Tableau ou grille de logos des technologies (Next.js, FastAPI, ThingsBoard, Pydantic, SQLite).

---

## 🖥️ Diapositive 9 : Qualité Logicielle & Audit Technique
*   **Rôle** : Valoriser la propreté du code et l'assurance qualité (très apprécié par le jury !).
*   **Titre** : Ingénierie de Code & Robustesse
*   **Contenu Textuel (Les Améliorations de l'Audit)** :
    *   🛠️ **Refactoring Architectural** : Suppression de l'anti-pattern "God Object" au profit d'un découpage strict en couches (*Routers, Services, Schemas, Core, Utils*).
    *   🔒 **Sécurité Renforcée** : Intégration d'une authentification sécurisée par jetons cryptographiques **JWT** asynchrones.
    *   🧪 **Couverture de Tests** : Endpoints documentés via Swagger et validés à 100% par des scénarios de tests d'intégration sous **Postman**.
*   **Visuels** : Petite capture propre d'une interface Swagger API ou d'un rapport Postman "200 OK" valide.

---

## 🖥️ Diapositive 10 : Transition Démo Live (Application sur Site)
*   **Rôle** : Indiquer visuellement que vous allez quitter le diaporama pour une démonstration pratique.
*   **Titre** : Démonstration Pratique (Live Demo)
*   **Contenu Textuel (Les étapes de la démo)** :
    1.  *Connexion & Recherche d'Entrepôt* (Optimization Lab).
    2.  *Interaction intelligente avec le chatbot* (OptiBot).
    3.  *Simulation de panne thermique et alerte d'urgence en direct* (Sentinel IoT).
*   **Visuels** : Un visuel central très épuré (icône d'écran ou d'ordinateur portable) avec le texte *"Démonstration en direct de la plateforme"*.

---

## 🖥️ Diapositive 11 : Perspectives et Conclusion
*   **Rôle** : Conclure la présentation sur une note d'ouverture technologique et d'ambition.
*   **Titre** : Bilan & Perspectives Futures
*   **Contenu Textuel** :
    *   📊 **Bilan** : Un MVP stable, robuste et hautement intégré, validé par des tests complets.
    *   🔗 **Perspectives : Traçabilité Blockchain** : Utilisation de Smart Contracts pour stocker les empreintes des logs de capteurs IoT, rendant l'historique de température infalsifiable face aux compagnies d'assurance.
    *   📱 **Perspectives : Application Mobile** : Version native pour les chauffeurs routiers permettant le suivi GPS et les accusés de livraison en direct.
*   **Visuels** : Deux colonnes avec d'un côté les points du bilan (vert émeraude) et de l'autre les perspectives futures.
