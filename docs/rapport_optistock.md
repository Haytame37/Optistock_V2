# Rapport de Projet : OptiStock Solutions
**Optimisation Logistique, Monitoring IoT et Intelligence Artificielle**

---

## Sommaire Résumé
OptiStock est une plateforme intégrée de gestion logistique qui répond à trois problématiques majeures du secteur au Maroc : la difficulté de mise en relation entre offreurs et demandeurs de stockage, le manque de suivi rigoureux de la conformité environnementale (IoT), et l'absence d'outils mathématiques pour l'optimisation des flux. Ce rapport détaille la conception, les choix technologiques et la réalisation de cette solution innovante.

---

## Chapitre 1 : Introduction et Analyse du Besoin

### 1.1 Introduction
Dans un monde où la rapidité et la qualité de la chaîne logistique déterminent la compétitivité d'une entreprise, OptiStock se positionne comme un tiers de confiance technologique. La plateforme permet aux propriétaires d'entrepôts de valoriser leurs espaces et aux chercheurs de trouver l'emplacement idéal grâce à l'IA et au suivi IoT en temps réel.

### 1.2 Analyse Concurrentielle (Avantages et Inconvénients)

| Caractéristiques | OptiStock | Plateformes Classiques (Annuaires) | Solutions de Monitoring Seules |
| :--- | :--- | :--- | :--- |
| **Matching IA** | ✅ Oui (Algorithmes d'optimisation) | ❌ Non (Simple recherche) | ❌ Non |
| **Monitoring IoT** | ✅ Intégré (Directement lié au bail) | ❌ Non | ✅ Oui (Mais isolé) |
| **Chatbot Dédié** | ✅ Oui (OptiBot multi-rôles) | ❌ Non | ❌ Non |
| **Transparence** | ✅ Totale (Données capteurs partagées) | ❌ Limitée | ✅ Moyenne |

**Nos Avantages :**
- **Interconnectivité** : L'alerte IoT est directement envoyée au chercheur (locataire), garantissant une confiance maximale.
*   **Aide à la décision** : L'Optimization Lab utilise des modèles mathématiques pour réduire les coûts de transport.
*   **Accessibilité** : Interface moderne et réactive (Next.js) adaptée à tous les terminaux.

**Nos Inconvénients (Limites actuelles) :**
- **Dépendance Réseau** : Nécessite une connexion continue pour le monitoring ThingsBoard.
*   **Hardware** : Demande un investissement initial en capteurs (ESP32/Proteus) pour les propriétaires.

### 1.3 Analyse des Besoins
**Besoins Fonctionnels :**
- **Gestion Multi-utilisateurs** : Authentification sécurisée (JWT) pour Propriétaires, Chercheurs et Admins.
*   **Moteur de Recherche Spatial** : Filtrage par localisation, prix et type de stockage.
*   **Système de Messagerie** : Négociation directe et suppression sécurisée de l'historique.
*   **Sentinel IoT** : Détection automatique des dépassements de seuils (Température/Humidité) avec alertes emails.

**Besoins Non-Fonctionnels :**
- **Réactivité** : Mise à jour des données IoT en moins de 3 secondes.
*   **Sécurité** : Protection des données sensibles et intégrité de la base de données SQLite.
*   **Esthétique** : Interface premium pour inspirer confiance aux partenaires industriels.

---

## Chapitre 2 : Conception du Système et Choix Technologiques

### 2.1 Choix Technologiques
Le choix d'une architecture découplée a été privilégié pour garantir la scalabilité et la performance.

- **Backend (FastAPI - Python)** : Choisi pour sa rapidité d'exécution et son support natif de l'asynchrone. Idéal pour traiter les flux IoT et les calculs d'IA.
- **Frontend (Next.js 14 - React)** : Utilisation des "Server Components" et de "TailwindCSS" pour une interface fluide, ultra-réactive et esthétique.
- **IoT (ThingsBoard & Proteus)** : ThingsBoard agit comme le concentrateur de données (Gateway), tandis que Proteus simule les capteurs industriels réels.
- **Base de Données (SQLite)** : Un choix pragmatique pour ce prototype, offrant une portabilité totale sans sacrifier la rigueur relationnelle.

### 2.2 Intelligence Artificielle : OptiBot
Le chatbot **OptiBot** n'est pas un simple moteur de recherche. Il utilise l'API **Google Gemini Pro** pour :
- Analyser le contexte de l'utilisateur (Propriétaire vs Chercheur).
- Fournir des conseils sur l'optimisation des stocks.
- Guider l'utilisateur dans l'utilisation des modules complexes comme l'Optimization Lab.

### 2.3 Logique Mathématique d'Optimisation
Le module "Optimization Lab" repose sur un algorithme de score pondéré :
- **Critère Distance (40%)** : Calcul par rapport aux points de livraison.
- **Critère Coût (30%)** : Ratio prix/surface.
- **Critère Qualité (30%)** : Historique de stabilité IoT (Température/Humidité).

*Note : Le score est recalculé en temps réel selon les priorités définies par le chercheur.*

### 2.4 Modélisation UML
*(Insérez ici vos schémas pour illustrer la structure logique du système)*

#### 2.4.1 Diagramme de Cas d'Utilisation
`[IMAGE_UML_USE_CASE : Montrant les interactions Admin/Owner/Researcher]`

#### 2.4.2 Diagramme de Classes
`[IMAGE_UML_CLASS : Montrant les relations entre Users, Warehouses, Messages et IoT_Data]`

### 2.5 Architecture de la Base de Données
La base de données est structurée autour de 5 tables principales :
1. **Users** : Gestion des rôles et identifiants.
2. **Warehouses** : Caractéristiques physiques et géographiques des espaces.
3. **Contact_Requests** : Lien transactionnel entre chercheur et propriétaire.
4. **Chat_Messages** : Historique des négociations (avec suppression sécurisée).
5. **IoT_Logs** : Stockage tampon des alertes et relevés critiques.

---

## Chapitre 3 : Réalisation, Interfaces et Tests

### 3.1 Interfaces Utilisateurs (Frontend)
Le frontend a été conçu pour être intuitif et professionnel. Voici les écrans principaux à inclure dans votre démonstration :

#### 3.1.1 Dashboard de Monitoring IoT
C'est l'interface la plus technique. Elle affiche :
- Des jauges circulaires dynamiques pour la Température et l'Humidité.
- Un graphique temporel (Recharts) montrant l'évolution des conditions.
- **Le Système d'Alerte** : Une bannière rouge pulsante qui s'active en cas de dépassement, avec un compte à rebours avant l'envoi automatique d'un e-mail de secours.
`[IMAGE_INTERFACE_IOT_DASHBOARD]`

#### 3.1.2 Optimization Lab & Recherche
Permet aux chercheurs de visualiser les entrepôts sur une carte et d'obtenir un classement basé sur la logistique.
`[IMAGE_INTERFACE_SEARCH_WIZARD]`

#### 3.1.3 Messagerie Intégrée
Un système de chat complet permettant la négociation. Nous avons implémenté une fonctionnalité de **suppression d'historique** pour permettre aux utilisateurs de gérer leur confidentialité.
`[IMAGE_INTERFACE_CHAT]`

### 3.2 UI/UX et Animations
Pour offrir une expérience "Premium", nous avons utilisé **Framer Motion** pour :
- Des effets de "Lift" (soulèvement) sur les boutons au survol.
- Des transitions fluides entre les pages.
- Des notifications (Sonner) interactives pour les alertes critiques.

### 3.3 Documentation API (Swagger)
Le backend FastAPI génère automatiquement une documentation interactive accessible via `/docs`. 
`[IMAGE_SWAGGER_API : Capture de la documentation interactive]`

Les endpoints clés testés :
- `POST /warehouses/alert` : Déclenchement des alertes e-mail.
- `GET /iot/telemetry/{token}` : Récupération des flux ThingsBoard.
- `DELETE /messaging/request/{id}` : Suppression sécurisée de conversation.

### 3.4 Tests Postman
Tous les endpoints ont été validés via Postman pour garantir la robustesse des échanges JSON et la validité des tokens JWT.
`[IMAGE_POSTMAN_TESTS : Capture des tests de réussite 200 OK]`

### 3.5 Bibliothèques Clés utilisées
- **Frontend** : `lucide-react` (icônes), `recharts` (graphiques), `framer-motion` (animations), `sonner` (toasts).
- **Backend** : `fastapi`, `pydantic`, `python-dotenv`, `smtplib`.

---

## Conclusion et Perspectives
OptiStock réussit le pari de fusionner la logistique traditionnelle avec les technologies modernes de l'IoT et de l'IA. La plateforme offre une visibilité sans précédent sur les conditions de stockage et optimise les décisions stratégiques. 

**Perspectives futures :**
- Intégration de la Blockchain pour certifier l'historique de température (Smart Contracts).
- Développement d'une application mobile native pour les conducteurs de camions.

---
**Rapport généré pour le projet PFA - OptiStock 2026**
