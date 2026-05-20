# 🗣️ Script Oral de Soutenance : Discours Slide par Slide (PFE OptiStock)

Ce document contient le script oral exact de votre présentation. Chaque section correspond à une diapositive de votre support de présentation. L'accent est mis sur une **élocution fluide, naturelle, mais hautement technique et professionnelle**.

---

## 🗣️ Diapositive 1 : Page de Garde
**Temps estimé** : 45 secondes

> "Monsieur le Président, honorables membres du jury, bonjour. C'est un réel privilège de vous présenter aujourd'hui les résultats de mes travaux de fin d'études, intitulés **OptiStock**.
> 
> Ce projet s'attaque à des enjeux industriels concrets en proposant une plateforme web hautement intégrée dédiée à l'optimisation logistique, au monitoring par l'Internet des objets et à l'aide à la décision par l'intelligence artificielle générative. 
> 
> Développée dans le cadre de l'obtention de mon diplôme d'Ingénieur d'État, cette solution a été conçue pour combler un vide sur le marché logistique en unifiant le matériel et le logiciel au service de la performance des entreprises."

---

## 🗣️ Diapositive 2 : Sommaire (Agenda)
**Temps estimé** : 30 secondes

> "Pour guider notre présentation ce matin, nous suivrons un parcours logique structuré en six grandes étapes. 
> 
> Nous commencerons par analyser les défis logistiques réels qui ont motivé ce projet. Puis, je vous présenterai notre vision globale de la solution OptiStock. 
> 
> Nous ferons ensuite un zoom technique sur nos trois grandes chaînes de valeur fonctionnelles pour comprendre la circulation des flux de données. 
> 
> Après avoir détaillé notre architecture et nos choix technologiques, je réaliserai une démonstration pratique en direct sur site. Enfin, nous conclurons avec l'audit de qualité logicielle qui a consolidé notre système, et nous ouvrirons sur les perspectives d'avenir."

---

## 🗣️ Diapositive 3 : Le Contexte et la Problématique
**Temps estimé** : 1 minute 15 secondes

> "Commençons par le contexte logistique marocain. Actuellement, la gestion de la chaîne d'approvisionnement fait face à trois verrous critiques.
> 
> Le premier verrou est **l'opacité du stockage** : la mise en relation entre les propriétaires d'espaces vides et les entreprises qui cherchent à stocker est lente, informelle et manque de transparence sur la qualité.
> 
> Le second verrou, le plus sensible, est **la rupture de la chaîne du froid**. Pour les denrées périssables ou pharmaceutiques, le manque de suivi automatisé et en direct des conditions ambiantes cause chaque année des millions de dirhams de pertes sèches de marchandises.
> 
> Enfin, le troisième verrou concerne **les coûts de transport du dernier kilomètre**. Sans outils mathématiques pour guider rationnellement le choix d'un entrepôt en fonction des points de livraison, les entreprises choisissent des entrepôts sous-optimaux, ce qui fait exploser les coûts de carburant et de transport. C'est à la jonction de ces trois défis que se situe notre solution."

---

## 🗣️ Diapositive 4 : La Solution OptiStock
**Temps estimé** : 1 minute

> "Notre réponse à ces défis est **OptiStock** : un tiers de confiance technologique unifié. 
> 
> Au lieu de multiplier des logiciels isolés, notre plateforme propose un écosystème tripartite unique. 
> 
> D'une part, elle offre un **Marketplace intelligent** qui permet une mise en relation directe et sécurisée entre les propriétaires d'espaces et les chercheurs. 
> 
> D'autre part, elle intègre une **sentinelle IoT** qui capture et surveille de manière ininterrompue les courbes de température et d'humidité. 
> 
> Enfin, elle intègre un **Optimization Lab** et un copilote conversationnel par IA pour transformer les relevés bruts et les contraintes logistiques en décisions stratégiques optimales."

---

## 🗣️ Diapositive 5 : Chaîne de Valeur n°1 – Sentinel IoT (Pipeline Complet)
**Temps estimé** : 1 minute 30 secondes

> "Analysons maintenant notre première grande chaîne de valeur : le pipeline IoT et le système Sentinel Alerting.
> 
> La donnée environnementale brute est captée sur site (simulée via Proteus et des protocoles de communication matériels de type ESP32). Elle transmet en temps réel les séries temporelles de température et d'humidité.
> 
> Cette télémétrie est ingérée de façon hautement sécurisée par notre Gateway IoT, **ThingsBoard**, qui gère l'authentification et l'historisation. 
> 
> Notre back-end FastAPI agit comme un relais asynchrone pour consommer ces données et les transmettre en direct au front-end Next.js, qui les affiche instantanément sous forme de graphiques temporels interactifs.
> 
> Surtout, nous avons développé le module **Sentinel IoT** : un moteur de règles en tâche de fond. Si une déviation thermique franchit un seuil critique défini, le système déclenche immédiatement un protocole d'alerte visuelle sur le dashboard et initie un envoi d'email automatique par protocole SMTP. Cette programmation asynchrone garantit que l'alerte est expédiée instantanément sans perturber le thread web principal du serveur."

---

## 🗣️ Diapositive 6 : Chaîne de Valeur n°2 – L'Optimization Lab
**Temps estimé** : 1 minute 15 secondes

> "Notre seconde chaîne de valeur est le moteur d'optimisation de l'**Optimization Lab**. 
> 
> Le choix d'un entrepôt ne doit pas se faire au hasard. C'est pourquoi nous avons modélisé un algorithme de score décisionnel multicritères pondéré. 
> 
> Ce score, calculé en temps réel sur une échelle de 0 à 100, s'appuie à 40 % sur la distance physique séparant l'entrepôt des points de livraison de l'entreprise. Cette distance est calculée via la **formule géodésique de Haversine** pour intégrer la courbure de la Terre. 
> 
> Nous y associons un critère de rentabilité financière à hauteur de 30 %, basé sur le ratio prix-surface, et un critère de fiabilité physique à hauteur de 30 %, évalué sur la stabilité historique des capteurs IoT de l'entrepôt. 
> 
> Sous le capot, nous intégrons le solveur MIP de recherche opérationnelle de Google OR-Tools pour résoudre les allocations logistiques de manière mathématiquement prouvée."

---

## 🗣️ Diapositive 7 : Chaîne de Valeur n°3 – L'Assistance IA Contextuelle
**Temps estimé** : 1 minute

> "Notre troisième chaîne de valeur introduit l'intelligence artificielle générative à travers l'agent **OptiBot**. 
> 
> Nous avons voulu dépasser le simple concept de chatbot textuel passif. Grâce à l'intégration de l'API de pointe **Google Gemini Pro**, nous avons structuré des prompts dynamiques dotés d'une **conscience de rôle**.
> 
> Si l'utilisateur connecté est un propriétaire d'entrepôt, OptiBot se comporte comme un ingénieur de maintenance et de rentabilité pour l'aider à valoriser son espace. 
> 
> S'il s'agit d'un chercheur, l'agent se transforme en conseiller logistique spécialisé, lui indiquant par exemple les régulations thermiques optimales pour conserver des fruits ou des produits pharmaceutiques. Cela apporte une véritable ergonomie intelligente et contextuelle à l'application."

---

## 🗣️ Diapositive 8 : Architecture Technique & Choix Technologiques
**Temps estimé** : 1 minute

> "Pour donner vie à ces flux de données complexes, nous avons mis en œuvre une stack technologique moderne et robuste.
> 
> Le front-end repose sur **Next.js 14** et React, nous permettant d'exploiter les Server Components pour des raisons de performance d'affichage et de protection stricte de nos secrets et clés d'API en arrière-plan.
> 
> Le back-end est propulsé par **FastAPI** en Python. Ce choix s'est avéré crucial pour deux raisons : sa vitesse d'exécution asynchrone exceptionnelle grâce au standard ASGI, indispensable pour notre pipeline IoT, et sa compatibilité native avec les bibliothèques d'optimisation mathématique et d'intelligence artificielle.
> 
> Côté persistance, la base de données relationnelle **SQLite** nous offre une portabilité totale, facilitant le déploiement rapide de notre MVP tout en maintenant l'intégrité relationnelle SQL standard."

---

## 🗣️ Diapositive 9 : Qualité Logicielle & Audit Technique
**Temps estimé** : 1 minute 15 secondes

> "Au-delà des fonctionnalités, nous avons accordé une importance majeure à l'ingénierie et à la qualité de notre code. 
> 
> Durant notre cycle de développement, nous avons mené un audit technique complet de notre back-end. Nous avons ainsi résolu l'anti-pattern monolithique du 'God Object' en divisant les fonctionnalités géantes en modules découplés selon le principe de séparation des responsabilités. 
> 
> La sécurité a été rehaussée par le hachage sécurisé des mots de passe avec sel et l'implémentation de sessions basées sur des tokens asynchrones cryptés **JWT**. 
> 
> Enfin, chaque route d'API a été documentée via Swagger et rigoureusement testée de bout en bout avec **Postman**, garantissant la stabilité structurelle du système."

---

## 🗣️ Diapositive 10 : Transition Démo Live (Application sur Site)
**Temps estimé** : 3 minutes (pendant la démonstration)

> "Afin de vous illustrer concrètement la réactivité de notre système, je vous propose de quitter notre support visuel pour effectuer une démonstration rapide en direct des trois chaînes de valeur de la plateforme..."
> 
> *(Consultez le document `docs/PRESENTATION_SOUTENANCE.md` pour le scénario pas-à-pas de la démo en direct : Connexion ➔ Recherche d'entrepôt ➔ Chat avec OptiBot ➔ Dépassement de seuil IoT et réception de l'alerte email)*.

---

## 🗣️ Diapositive 11 : Perspectives et Conclusion
**Temps estimé** : 1 minute

> "Pour conclure, OptiStock a prouvé sa capacité à unifier avec succès le monitoring matériel de l'IoT et la puissance d'analyse logicielle des mathématiques et de l'IA au sein d'une Clean Architecture stable.
> 
> Les perspectives de notre projet s'orientent vers deux axes. Le premier est la **traçabilité par Blockchain**, qui permettra de sceller de manière infalsifiable les logs de température IoT dans des Smart Contracts pour certifier la chaîne du froid auprès des assurances en cas de litige. Le second axe est le développement d'une **application mobile native** dédiée aux transporteurs pour intégrer la géolocalisation et le suivi du dernier kilomètre.
> 
> Je vous remercie infiniment pour votre attention, et je suis désormais ravi de répondre à vos questions et d'échanger avec vous."
