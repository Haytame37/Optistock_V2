# 🎓 Guide de Soutenance PFE : OptiStock Solutions
**Optimisation Logistique, Monitoring IoT et Intelligence Artificielle**

Ce document est votre guide ultime pour réussir votre présentation de fin d'études. Il contient la structure complète de votre diaporama (12 diapositives), le script oral exact à réciter, des conseils visuels et une préparation intense aux questions du jury.

---

## 📅 Structure du Diaporama & Script Oral

### 🖥️ Diapositive 1 : Page de Garde
* **Titre de la slide** : Projet de Fin d'Études – OptiStock : Plateforme Intégrée de Gestion Logistique, Monitoring IoT et Intelligence Artificielle.
* **Visuels** : Logo de votre établissement, une capture élégante du Dashboard OptiStock en arrière-plan semi-transparent, vos noms (candidat et encadrants).
* **Mots clés à l'écran** : *Optimisation Logistique*, *Internet des Objets (IoT)*, *Recherche Opérationnelle*, *IA Générative*.

#### 🗣️ Script Oral :
> "Monsieur le Président, Honorables membres du jury, bonjour. C'est avec un grand plaisir que je me tiens devant vous aujourd'hui pour vous présenter mon projet de fin d'études intitulé **OptiStock**. Ce projet s'inscrit au carrefour de trois révolutions technologiques majeures : l'Internet des objets pour le monitoring industriel, la recherche opérationnelle pour l'optimisation des flux, et l'intelligence artificielle générative pour l'aide à la décision. Sous la direction de mes encadrants, j'ai conçu et développé une solution globale qui répond à des besoins critiques du secteur logistique."

---

### 🖥️ Diapositive 2 : Contexte et Problématique
* **Titre de la slide** : Contexte & Problématique Logistique.
* **Visuels** : Trois icônes ou graphiques simples :
  1. 🏢 *Marché opaque* : Difficulté pour les chercheurs d'entrepôts de trouver rapidement des espaces conformes et disponibles.
  2. 🌡️ *Ruptures de la chaîne du froid* : Manque de suivi en temps réel des conditions de stockage (température, humidité), causant des pertes sèches de marchandises sensibles (agroalimentaire, pharmaceutique).
  3. 🚛 *Coûts de transport élevés* : Absence d'outils d'aide à la décision mathématique pour minimiser les distances et optimiser les coûts de livraison.

#### 🗣️ Script Oral :
> "Aujourd'hui, le secteur logistique marocain fait face à trois défis majeurs. Premièrement, le marché du stockage souffre d'une opacité : la mise en relation entre propriétaires d'entrepôts et entreprises demandeuses est lente et informelle. Deuxièmement, le suivi de la conformité environnementale est souvent manuel, ce qui engendre des pertes de marchandises sensibles en cas de défaillance des systèmes de climatisation. Enfin, l'absence d'outils mathématiques d'aide à la décision conduit à des choix d'entrepôts non optimisés, faisant exploser les coûts de transport du dernier kilomètre. C'est pour résoudre ces trois problématiques de manière unifiée que nous avons conçu **OptiStock**."

---

### 🖥️ Diapositive 3 : La Solution OptiStock
* **Titre de la slide** : La Solution : Une Plateforme Tripartite Innovante.
* **Visuels** : Un diagramme circulaire ou à 3 piliers interconnectés :
  * **Pilier 1 : Le Marketplace Intelligent** (Mise en relation directe, transparence des baux, messagerie intégrée).
  * **Pilier 2 : Sentinel IoT** (Capteurs connectés, suivi en temps réel des courbes, système d'alerte automatique par email).
  * **Pilier 3 : Optimization Lab & IA** (Calcul du score de qualité et calcul d'itinéraires logistiques optimaux, chatbot assistant multi-rôles).

#### 🗣️ Script Oral :
> "OptiStock n'est pas un simple annuaire d'entrepôts, c'est un écosystème intelligent structuré autour de trois grands modules :
> 1. Un **Marketplace transparent** qui permet aux propriétaires de monétiser leurs espaces et aux locataires de négocier via un chat sécurisé.
> 2. Une **sentinelle IoT** qui capte et historise les données de température et d'humidité en temps réel, garantissant la conformité environnementale du stockage.
> 3. Et enfin, un **laboratoire d'optimisation** combinant des algorithmes de recherche opérationnelle pour le choix de l'entrepôt idéal et un agent d'intelligence artificielle pour guider les utilisateurs dans leurs décisions opérationnelles."

---

### 🖥️ Diapositive 4 : Spécification des Besoins
* **Titre de la slide** : Analyse des Besoins & Acteurs du Système.
* **Visuels** : Tableau comparatif ou diagramme représentant les 3 acteurs principaux :
  * 👑 **Administrateur** (Gestion de la plateforme, modération, monitoring global).
  * 🏭 **Propriétaire (Owner)** (Publication d'entrepôts, configuration des seuils de capteurs, suivi de ses espaces).
  * 🔬 **Chercheur (Researcher)** (Recherche d'espaces, calcul de l'itinéraire optimal, suivi IoT en direct du stock loué).

#### 🗣️ Script Oral :
> "Pour concevoir ce système, nous avons mené une analyse rigoureuse des besoins. La plateforme segmente l'expérience utilisateur en trois profils distincts. Le propriétaire peut configurer les seuils d'alerte spécifiques pour ses entrepôts selon la nature des produits stockés. Le chercheur dispose d'outils pour comparer scientifiquement les offres selon ses critères de coûts et de contraintes de transport. L'administrateur, quant à lui, garantit la sécurité et la modération de l'écosystème. Sur le plan non-fonctionnel, nous avons mis l'accent sur la réactivité avec un temps de réponse d'affichage IoT inférieur à 3 secondes, et sur la sécurité des données privées."

---

### 🖥️ Diapositive 5 : Choix Technologiques & Architecture
* **Titre de la slide** : Architecture Globale et Choix Technologiques.
* **Visuels** : Schéma d'architecture Client-Serveur découplée (Next.js 14 $\leftrightarrow$ FastAPI $\leftrightarrow$ SQLite + ThingsBoard IoT).
* **Mots clés** : *Architecture Découplée (SoC)*, *React Server Components*, *FastAPI ASGI*, *SQLite*, *ThingsBoard Gateway*.

#### 🗣️ Script Oral :
> "Afin de garantir l'évolutivité, la maintenabilité et la sécurité de notre plateforme, nous avons choisi une **architecture découplée de type Client-Serveur**. 
> Pour le Front-end, nous avons retenu **Next.js 14** basé sur React, exploitant les Server Components pour des performances optimales et une sécurité accrue de nos clés d'API.
> Pour le Back-end, le choix s'est porté sur **FastAPI** en Python. Ce choix est doublement motivé : d'une part, par son asynchronisme natif extrêmement performant pour les flux IoT, et d'autre part, par la richesse de l'écosystème Python pour l'intégration de nos modèles mathématiques et de l'API d'IA Google Gemini.
> Côté persistance, nous utilisons **SQLite**, un choix pragmatique garantissant une portabilité totale du prototype sans compromis sur l'intégrité relationnelle SQL."

---

### 🖥️ Diapositive 6 : Conception UML (Structure Logique)
* **Titre de la slide** : Modélisation et Conception Orientée Objet.
* **Visuels** : Version simplifiée et propre du Diagramme de Classes UML (focalisé sur les entités principales : `User`, `Warehouse`, `ContactRequest`, `ChatMessage`, `IoTLog`).

#### 🗣️ Script Oral :
> "La conception de notre base de données et de notre logique applicative repose sur une modélisation UML rigoureuse. Le diagramme de classes ici présenté montre comment nous lions les utilisateurs à leurs rôles, comment un entrepôt est associé à ses métriques géographiques et physiques, et comment le système d'alerte et l'historique des messages de négociation sont isolés pour assurer une stricte conformité. Cette structure évite les couplages forts et permet d'assurer des requêtes d'agrégation rapides."

---

### 🖥️ Diapositive 7 : Zoom Technique – Le Pipeline IoT et Sentinel Alerting
* **Titre de la slide** : Monitoring en Temps Réel et Pipeline Événementiel IoT.
* **Visuels** : Schéma du flux de données : 
  `Capteur (Proteus/ESP32) ➔ Télémétrie ➔ Gateway ThingsBoard ➔ FastAPI Relay ➔ Frontend (Recharts) ➔ Déclenchement d'Alerte Asynchrone (SMTP)`.

#### 🗣️ Script Oral :
> "Entrons maintenant dans le cœur technique de notre module IoT. Le flux commence au niveau physique ou simulé, où des capteurs environnementaux transmettent des données de température et d'humidité. C'est la plateforme industrielle **ThingsBoard** qui joue le rôle de Gateway IoT, sécurisant l'authentification des capteurs et stockant les séries temporelles. 
> Notre back-end FastAPI agit comme un proxy sécurisé, exposant ces flux au front-end qui les affiche sous forme de graphiques temporels interactifs. 
> Surtout, nous avons développé le module **Sentinel IoT** : un moteur de règles asynchrone qui, lors de la détection d'une anomalie environnementale, déclenche immédiatement un protocole d'alerte visuelle sur le dashboard et envoie un email d'urgence automatique au locataire, lui laissant le temps de sauver son stock."

---

### 🖥️ Diapositive 8 : Zoom Technique – Moteur d'Optimisation & IA
* **Titre de la slide** : Optimization Lab & Aide à la Décision IA.
* **Visuels** : La formule du score multicritères : 
  $$\text{Score} = (0.40 \times \text{Distance}) + (0.30 \times \text{Coût}) + (0.30 \times \text{Stabilité IoT})$$
  Une capture propre de l'agent **OptiBot** (Gemini Pro).

#### 🗣️ Script Oral :
> "Pour l'aide à la décision, nous avons développé deux modules intelligents.
> Le premier, l'**Optimization Lab**, repose sur un algorithme d'analyse multicritères pondéré. Il calcule en temps réel un score de pertinence pour chaque entrepôt en se basant à 40 % sur la distance géographique calculée via la formule Haversine, à 30 % sur le ratio coût/surface, et à 30 % sur la stabilité historique des capteurs IoT.
> Le second est **OptiBot**, un agent conversationnel avancé propulsé par **Google Gemini Pro**. Ce chatbot n'est pas passif : il est doté d'une conscience de rôle. Il sait si l'utilisateur est un propriétaire ou un chercheur d'entrepôt et adapte ses conseils logistiques et techniques en fonction de ce contexte métier spécifique."

---

### 🖥️ Diapositive 9 : Démonstration Pratique (Live Demo)
* **Titre de la slide** : Démonstration Pratique du Système.
* **Visuels** : Un visuel attrayant indiquant *"Démonstration en Direct"* avec 3 étapes listées :
  1. *Recherche et filtrage multicritères d'entrepôts*.
  2. *Discussion en temps réel avec OptiBot*.
  3. *Déclenchement et visualisation d'une alerte critique IoT en temps réel*.

#### 🗣️ Script Oral :
> "Pour vous prouver la viabilité et la robustesse de notre implémentation, je vous propose une démonstration rapide en direct des fonctionnalités clés de la plateforme..." *(Passez ici sur votre navigateur - voir la section Scénario de Démo ci-dessous)*.

---

### 🖥️ Diapositive 10 : Qualité Logicielle, Sécurité & Audit Technique
* **Titre de la slide** : Assurance Qualité & Sécurité.
* **Visuels** : Tableau récapitulatif de l'audit :
  * *Refactoring* : Suppression de l'anti-pattern "God Object" au profit d'une Clean Architecture découplée en Routers, Services, Schemas.
  * *Sécurité* : Mots de passe sécurisés par hachage fort, tokens de session JWT asynchrones.
  * *Tests* : Couverture des endpoints via **Swagger** et tests d'intégration automatisés validés par **Postman** (Status 200 OK).

#### 🗣️ Script Oral :
> "Durant le cycle de développement, nous avons accordé une importance capitale à l'assurance qualité et à l'ingénierie du code. Suite à un audit technique approfondi, nous avons totalement restructuré le code pour éliminer les anti-patterns de type 'God Object'. Nous avons séparé les responsabilités en modules distincts, renforcé la sécurité de l'authentification avec des jetons cryptographiques JWT, et validé rigoureusement chaque route d'API. L'intégralité de nos endpoints a été soumise à des tests de charge et d'intégration automatisés sous Postman, garantissant un comportement stable en toutes circonstances."

---

### 🖥️ Diapositive 11 : Conclusion et Perspectives
* **Titre de la slide** : Conclusion & Horizons futurs.
* **Visuels** : Deux colonnes claires :
  * **Bilan** : Une plateforme fonctionnelle qui unifie logistique, IoT et IA, validée techniquement.
  * **Perspectives** :
    1. *Blockchain* : Utilisation de Smart Contracts pour certifier de manière immuable l'historique de température IoT (confiance ultime assureur/locataire).
    2. *Application Mobile* : Version mobile pour les chauffeurs-livreurs et la gestion sur site.

#### 🗣️ Script Oral :
> "En conclusion, OptiStock a réussi son pari de transformer la gestion logistique traditionnelle en un écosystème connecté et intelligent. Nous sommes passés d'un prototype de recherche à un MVP robuste, stable et industrialisable.
> En termes de perspectives, nous envisageons d'intégrer la technologie Blockchain afin d'inscrire l'historique de température IoT dans des contrats intelligents infalsifiables pour rassurer les compagnies d'assurance. Nous prévoyons également le développement d'une application mobile dédiée aux chauffeurs pour optimiser la logistique du dernier kilomètre. Je vous remercie pour votre attention et je suis désormais à votre entière disposition pour répondre à vos questions."

---

## 🛠️ Scénario de Démonstration en Direct (Anti-Bug)

Pour captiver le jury et éviter l'effet "démo qui plante", suivez ce scénario millimétré de **3 minutes maximum** :

1. **La Recherche Spatiale (1 min)** :
   * Connectez-vous en tant que **Researcher**.
   * Allez sur le module de recherche d'entrepôt. Faites un filtrage rapide (ex: triez par prix ou par distance).
   * Dites : *"Ici, notre algorithme d'Optimization Lab classe instantanément les entrepôts selon le score logistique pondéré (coût, distance Haversine et fiabilité historique IoT)."*
2. **L'IA Conversationnelle (1 min)** :
   * Ouvrez l'interface d'**OptiBot**.
   * Posez une question métier simple en français (ex: *"Comment puis-je stocker des tomates en toute sécurité ?"*).
   * Montrez la réponse structurée fournie par Gemini Pro et dites : *"Comme vous pouvez le voir, l'agent IA intègre le contexte utilisateur et fournit des recommandations logistiques et de régulation de température adaptées."*
3. **Le Clou du Spectacle : L'Alerte IoT (1 min)** :
   * Affichez la page du **Dashboard IoT**.
   * Déclenchez ou simulez un dépassement de seuil de température (ex: passez à 28°C sur vos données de capteurs).
   * Montrez la **bannière rouge pulsante** et le compte à rebours interactif qui s'affichent sur Next.js avec une notification toast.
   * Dites : *"Le système Sentinel IoT a instantanément capté l'anomalie environnementale. Il lance un compte à rebours de sécurité visible sur le dashboard et envoie de manière totalement asynchrone un email d'alerte par SMTP pour notifier les responsables de l'entrepôt."*

---

## ❓ Préparation aux Questions du Jury (FAQ Blindée)

Voici les 10 questions techniques et conceptuelles les plus fréquentes que le jury pourrait vous poser, accompagnées des réponses parfaites :

### Q1 : "Pourquoi avoir choisi FastAPI au lieu de Django ou Flask ?"
* **Mauvaise réponse** : *"Parce que c'était plus simple ou moderne."*
* **Réponse du Pro** : *"FastAPI est un framework asynchrone basé sur le standard ASGI, contrairement à Flask ou Django (historiquement WSGI). Cette capacité asynchrone est indispensable dans notre cas pour gérer efficacement des tâches concurrentes comme l'écoute des flux de télémétrie IoT et l'envoi d'e-mails en tâche de fond sans bloquer les requêtes des utilisateurs. De plus, sa validation de données native basée sur Pydantic nous assure un typage fort et robuste, et la génération automatique de sa documentation Swagger a accéléré notre phase de test."*

### Q2 : "Comment gérez-vous la sécurité de l'authentification et des données ?"
* **Réponse du Pro** : *"Nous utilisons le standard industriel **OAuth2** avec des jetons de session **JWT (JSON Web Tokens)** signés cryptographiquement. Les mots de passe ne sont jamais stockés en clair dans la base de données SQLite : ils sont hachés de manière sécurisée grâce à un algorithme de dérivation de clé fort avec sel. De plus, nous appliquons une vérification stricte des droits au niveau des routeurs FastAPI pour interdire l'accès à un rôle non autorisé (ex: un locataire ne peut pas modifier les seuils IoT d'un entrepôt qui ne lui appartient pas)."*

### Q3 : "SQLite est une base de données légère. Est-elle adaptée pour de la production industrielle ?"
* **Réponse du Pro** : *"SQLite a été retenue pour ce prototype car elle offre une portabilité totale sans configuration complexe de serveurs, ce qui est idéal pour les démonstrations académiques et le déploiement local rapide. Cependant, notre architecture respecte scrupuleusement la séparation des préoccupations. Toutes nos interactions de base de données passent par un gestionnaire centralisé et standardisé. Migrer vers un serveur de niveau industriel comme **PostgreSQL** ou **MySQL** ne demande aucune réécriture de code, mais simplement le changement de la chaîne de connexion dans notre fichier de configuration `.env`."*

### Q4 : "Qu'est-ce que ThingsBoard apporte par rapport à une base de données classique pour l'IoT ?"
* **Réponse du Pro** : *"ThingsBoard est un concentrateur et un broker IoT spécialisé. Utiliser une base de données SQL classique pour stocker chaque milliseconde de télémétrie sature rapidement le disque en requêtes d'écriture. ThingsBoard offre : 1) Une gestion native des équipements (Device Management) et de leur sécurité par jetons individuels, 2) Une base de données optimisée pour les séries temporelles, et 3) Un moteur de règles visuel permettant de prétraiter les données avant de les relayer à notre backend, ce qui allège la charge de notre serveur FastAPI."*

### Q5 : "Si la connexion réseau est coupée, comment gérez-vous la perte de données IoT ?"
* **Réponse du Pro** : *"C'est une excellente question qui touche à la résilience matérielle. Dans notre architecture, si le réseau coupe entre notre passerelle (ESP32/ThingsBoard) et le backend, le microcontrôleur local (ou le simulateur) est conçu pour mettre en mémoire tampon (Buffer local) les dernières mesures. Dès que la connexion est rétablie, ces données historiques sont envoyées en rafale pour combler le vide temporel. C'est l'un des grands avantages d'utiliser ThingsBoard qui gère nativement ce rattrapage d'historique."*

### Q6 : "Comment fonctionne concrètement votre algorithme d'optimisation (Optimization Lab) ?"
* **Réponse du Pro** : *"Notre moteur d'aide à la décision repose sur une analyse décisionnelle multicritères (MCDA). Nous calculons un score pondéré sur une échelle de 0 à 100. La distance géographique est calculée dynamiquement entre les coordonnées GPS de l'entrepôt et du point de livraison en utilisant la **formule trigonométrique de Haversine** pour tenir compte de la courbure de la Terre. Nous croisons ensuite cette donnée avec le ratio prix-surface et l'indice de stabilité des capteurs (le ratio de temps passé sous les seuils requis). Les poids (40-30-30) peuvent être dynamiquement ajustés selon la priorité du chercheur."*

### Q7 : "Pourquoi utiliser Gemini Pro pour le Chatbot au lieu d'un simple moteur de recherche textuel ?"
* **Réponse du Pro** : *"Un moteur de recherche classique est incapable de comprendre l'intention ou le contexte métier de l'utilisateur. En intégrant **Google Gemini Pro** via son API, nous bénéficiens d'un modèle linguistique de pointe. Nous lui injectons un 'System Prompt' qui définit son rôle (conseiller logistique) et lui passons le contexte de l'utilisateur connecté. Ainsi, s'il détecte un chercheur de denrées périssables, il va proactivement l'orienter vers les critères de température IoT requis, apportant une réelle valeur ajoutée ergonomique."*

### Q8 : "Quelle a été la plus grande difficulté technique rencontrée lors du projet ?"
* **Réponse du Pro** : *"Notre plus grand défi a été la synchronisation asynchrone et en temps réel de notre pipeline d'alertes. Il fallait s'assurer que lorsqu'un capteur dévie, le front-end Next.js affiche immédiatement l'alerte de manière réactive, tandis que le serveur FastAPI envoie le courriel d'avertissement en arrière-plan, le tout sans ralentir ou bloquer les autres utilisateurs connectés. Nous avons résolu cela en concevant un moteur de services asynchrone utilisant la programmation concurrente sous Python (Async/Await) et des requêtes d'écoute réactives côté client."*

### Q9 : "Quels ont été les résultats de votre audit technique ?"
* **Réponse du Pro** : *"L'audit technique nous a permis de passer d'un prototype de recherche (MVP) à un code de niveau industriel. Nous avons résolu le problème de la centralisation excessive en éclatant le code monolithique en architectures modulaires par couches. Nous avons également corrigé les failles de sécurité en remplaçant les méthodes de hachage obsolètes par du hachage avec sel et des jetons JWT sécurisés, et nous avons systématisé l'utilisation de modèles Pydantic pour garantir le typage de nos données."*

### Q10 : "Quelles perspectives voyez-vous à votre projet à moyen terme ?"
* **Réponse du Pro** : *"La perspective la plus prometteuse est l'intégration de la **Blockchain Ethereum ou Hyperledger**. En stockant les empreintes cryptographiques (hashes) de nos données de température IoT dans la blockchain à intervalles réguliers, nous offrons une preuve infalsifiable des conditions de stockage. Cela permettrait d'automatiser le remboursement d'assurances en cas de rupture de la chaîne du froid grâce à des Smart Contracts. La seconde perspective est le développement d'une application mobile native pour les chauffeurs afin d'intégrer le suivi GPS de la livraison en direct."*
