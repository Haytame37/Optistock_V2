# OptiStock Solutions - Documentation fonctionnelle longue pour une autre IA

## 1. Vue d'ensemble du systeme

OptiStock Solutions est une application Streamlit de supervision, d'analyse et d'aide a la decision pour des entrepots relies a des donnees IoT. Le systeme a ete construit autour de trois profils principaux :

- `admin`
- `chercheur`
- `proprietaire`

L'objectif global de la plateforme est de :

- gerer des comptes utilisateurs par role
- exploiter des donnees d'entrepots et des historiques capteurs
- analyser temperature et humidite
- produire des indicateurs de fiabilite et de conformite
- aider a la recommandation et a la decision

Le projet combine donc :

- authentification
- routage par role
- lecture de donnees CSV et SQLite
- traitement du signal IoT
- scoring environnemental et logistique
- interfaces metier dediees a chaque role

Cette documentation est destinee a une autre IA afin qu'elle puisse comprendre le systeme existant avant d'ajouter de nouvelles fonctionnalites sans casser l'existant.

---

## 2. Structure generale du projet

Les points d'entree les plus importants sont :

- `app.py`
- `pages/2_Dashboard_Admin.py`
- `pages/3_Interface_Chercheur.py`
- `pages/4_Interface_Proprietaire.py`
- `core/auth.py`
- `core/scoring.py`
- `core/iot_analysis.py`
- `core/warehouse_search.py`
- `core/proprietaire_analysis.py`

Les donnees sont principalement stockees dans :

- `data/cleaned/`
- `data/samples/`

La base SQLite est stockee dans :

- `database/optistock.db`

---

## 3. Fonctionnalites globales du systeme

Le systeme fournit actuellement les grandes familles de fonctionnalites suivantes :

### 3.1 Authentification et gestion des roles

Le systeme permet :

- la connexion par nom d'utilisateur / mot de passe
- la gestion d'une session utilisateur via Streamlit
- la redirection automatique selon le role
- la protection des pages selon les droits

Les roles actuellement utilises sont :

- `admin`
- `chercheur`
- `proprietaire`

La logique d'authentification est concentree dans :

- `core/auth.py`

### 3.2 Gestion des comptes

Le systeme permet deja :

- creation d'un compte
- modification d'un compte
- reinitialisation du mot de passe
- suppression d'un compte
- activation / desactivation
- attribution d'un identifiant incremental `user_id`

Les comptes sont stockes dans la table SQLite :

- `utilisateurs`

### 3.3 Analyse des donnees entrepots

Le projet lit les donnees des entrepots a partir de fichiers CSV, principalement :

- `data/cleaned/entrepots.csv`

Chaque entrepot est associe a :

- un `id_entrepot`
- un `id_proprietaire`
- des coordonnees geographiques

### 3.4 Analyse des historiques IoT

Chaque entrepot peut avoir deux historiques :

- temperature
- humidite

Les donnees capteurs sont organisees dans des fichiers comme :

- `temperature_ENT001.csv`
- `humidite_ENT001.csv`

Chaque historique contient en general :

- `datetime`
- `capteur1`
- `capteur2`
- `capteur3`

### 3.5 Scoring et aide a la decision

Le systeme inclut :

- un score environnemental
- une analyse saisonniere
- une logique de fusion logistique / environnement
- une recommandation intelligente finale

---

## 4. Fonctionnalites par role

## 4.1 Role Admin

La page principale de l'administrateur est :

- `pages/2_Dashboard_Admin.py`

### Fonctionnalites actuelles de l'admin

L'admin peut :

- consulter la liste des entrepots
- filtrer les entrepots par proprietaire ou type
- voir des indicateurs de synthese
- gerer les comptes utilisateurs
- generer automatiquement des comptes proprietaire a partir des `id_proprietaire`
- consulter un tableau de synthese des capteurs par proprietaire

### Informations visibles pour l'admin

L'admin voit notamment :

- le nombre d'entrepots
- le nombre total de comptes actifs
- le nombre de chercheurs en base
- le nombre de proprietaires en base
- un tableau de comptes avec :
  - `user_id`
  - `username`
  - `full_name`
  - `role`
  - `is_active`
  - `created_at`

### Gestion des comptes dans l'admin

L'administrateur peut :

- creer un compte chercheur
- creer un compte proprietaire
- modifier un compte existant
- modifier le role
- modifier le nom complet
- activer / desactiver un compte
- redefinir un mot de passe
- supprimer un compte

### Generation automatique des comptes proprietaire

Le systeme est capable de :

- lire les `id_proprietaire` depuis `entrepots.csv`
- generer un compte pour chaque proprietaire absent

Regle actuelle :

- `OWN003` devient `own003`
- mot de passe temporaire : `own003@123`

---

## 4.2 Role Chercheur

La page du chercheur est :

- `pages/3_Interface_Chercheur.py`

### Fonctionnalites actuelles du chercheur

Le chercheur dispose principalement de modules d'analyse et de recommandation.

Dans cette interface, il peut :

- importer des fichiers CSV
- lancer des analyses
- effectuer des traitements multi-entrepots
- faire de l'optimisation d'emplacement
- travailler sur des recommandations d'entrepots

### Objectif metier du chercheur

Le chercheur agit comme un profil analytique. Son interface sert a :

- explorer des donnees
- tester des scenarios
- produire des recommandations logistiques
- analyser la conformite IoT

Le role chercheur est donc plus oriente :

- data analysis
- optimisation
- scoring
- exploration metier

---

## 4.3 Role Proprietaire

La page du proprietaire est :

- `pages/4_Interface_Proprietaire.py`

### Fonctionnalites actuelles du proprietaire

Apres connexion, un proprietaire peut :

- voir son identifiant proprietaire
- voir la liste de ses entrepots
- consulter un resume important par entrepot
- selectionner un entrepot
- voir l'analyse detaillee de cet entrepot
- consulter les historiques temperature et humidite
- visualiser un graphe saisonnier

### Liaison entre compte et donnees

Le systeme lie le compte a ses donnees ainsi :

- `own003` est converti en `OWN003`
- `OWN003` est recherche dans `entrepots.csv`

Ainsi, le compte proprietaire `own003` n'affiche que les entrepots associes a `OWN003`.

### Informations visibles dans l'interface proprietaire

Le proprietaire voit :

- ses entrepots
- un tableau resume par entrepot
- les deltas jour / nuit
- le nombre de valeurs manquantes
- le nombre de valeurs hors limite
- la fiabilite temperature
- la fiabilite humidite
- l'etat par saison
- un graphe des differences saisonnieres
- l'historique temperature
- l'historique humidite

---

## 5. Fonctionnalites d'analyse IoT

Le systeme comporte plusieurs couches d'analyse IoT.

## 5.1 Chargement des donnees

Les historiques sont lus a partir des CSV.

Les fonctions de chargement nettoient en general :

- les colonnes
- la date / heure
- l'ordre chronologique

## 5.2 Traitement du signal

Le traitement du signal est principalement gere dans :

- `core/scoring.py`
- `core/iot_analysis.py`

Le pipeline inclut :

- interpolation des valeurs manquantes
- lissage par moyenne mobile
- agregat multi-capteurs

### Interpolation

Les valeurs manquantes peuvent etre comblees pour stabiliser la serie temporelle.

### Lissage

Le bruit des capteurs est reduit par une moyenne glissante.

### Agregation multi-capteurs

Lorsqu'un historique contient :

- `capteur1`
- `capteur2`
- `capteur3`

le systeme calcule souvent une valeur moyenne par ligne afin d'obtenir un signal plus robuste.

---

## 5.3 Detection des anomalies

Le systeme detecte des anomalies sur :

- temperature
- humidite

Il compare les valeurs a :

- des bornes globales
- ou des bornes saisonnieres

Cela permet d'identifier :

- les depassements
- les phases instables
- les donnees non conformes

---

## 5.4 Analyse saisonniere

Le projet tient compte des saisons via :

- `NORMES_SAISONNIERES`

Chaque mois a :

- une plage temperature minimale / maximale
- une plage humidite minimale / maximale

L'analyse saisonniere sert a produire :

- une moyenne mensuelle
- un nombre de points hors norme
- un etat du mois

Les etats utilises sont par exemple :

- `Conforme`
- `Vigilance`
- `Hors limite`

---

## 6. Fonctionnalites de scoring

Le fichier central pour le scoring est :

- `core/scoring.py`

### 6.1 Score environnemental

Le score environnemental repose sur :

- le nombre de releves
- le nombre d'anomalies temperature
- le nombre d'anomalies humidite

Le score est calcule sur 100.

### 6.2 Normalisation

Le systeme normalise certains criteres afin d'eviter les biais d'unites.

Exemples :

- distance
- score IoT

### 6.3 Fusion SAW

Le score final suit une fusion de type SAW :

- `60% logistique`
- `40% environnement`

Cette logique est utilisee pour produire une note globale d'aide a la decision.

### 6.4 Recommandation intelligente

Le systeme genere ensuite :

- un statut
- une interpretation
- une action recommandee
- une alerte saisonniere

---

## 7. Fonctionnalites de recherche et recommandation d'entrepots

Le module principal est :

- `core/warehouse_search.py`

### Fonctionnalites actuelles

Ce module permet :

- de charger les historiques d'un entrepot
- de mesurer sa robustesse
- de calculer un score
- de classer plusieurs entrepots

### Penalites prises en compte

Le score d'un entrepot depend notamment de :

- la disponibilite des donnees
- la coherence entre capteurs
- l'instabilite du signal
- les incidents
- la compatibilite avec le type de stockage

---

## 8. Module proprietaire_analysis

Le module :

- `core/proprietaire_analysis.py`

a ete cree pour alimenter l'interface proprietaire.

### Fonctionnalites fournies

Il calcule :

- l'analyse par proprietaire
- l'analyse par entrepot
- les deltas jour / nuit
- la fiabilite des donnees
- l'etat saisonnier

### Indices calcules

#### Difference jour / nuit

Le systeme compare la moyenne des valeurs :

- de jour
- de nuit

Cela sert a detecter des ecarts de comportement selon la periode.

#### Fiabilite

La fiabilite brute est calculee a partir :

- des valeurs manquantes
- des valeurs hors limites
- du nombre total de valeurs

#### Etat par saison

Le systeme calcule, par mois :

- la temperature moyenne
- l'humidite moyenne
- les hors limites temperature
- les hors limites humidite
- le statut du mois

### Important : deux logiques de comptage coexistent

Il faut bien comprendre qu'il existe deux niveaux de mesure :

#### 1. Fiabilite brute

La fonction `compute_data_reliability(...)` travaille sur les colonnes brutes :

- `capteur1`
- `capteur2`
- `capteur3`

Chaque cellule est comptee.

Donc les totaux peuvent etre tres grands.

#### 2. Etat saisonnier

La fonction `compute_season_state(...)` travaille sur une valeur moyenne par timestamp.

Donc les nombres affiches dans le tableau saisonnier peuvent etre tres differents des metriques de fiabilite brute.

Cette difference est normale dans le systeme actuel.

---

## 9. Sources de donnees

Le projet utilise principalement deux sources :

### 9.1 CSV

Source la plus utilisee actuellement dans l'interface :

- `data/cleaned/`
- `data/samples/`

Les pages proprietaire et admin s'appuient fortement sur ces donnees.

### 9.2 SQLite

Utilisee surtout pour :

- les comptes utilisateurs
- certaines lectures de donnees si disponibles

Le projet n'est pas encore totalement migre vers SQLite. Une autre IA doit donc faire attention a ne pas supposer qu'une seule source est utilisee partout.

---

## 10. Masquage de la sidebar

Le systeme cache volontairement la sidebar Streamlit par CSS.

Cela signifie que :

- la navigation se fait sans barre laterale visible
- les informations de session sont affichees dans la page elle-meme

Une autre IA ne doit pas reintroduire la sidebar sans verifier l'impact UX.

---

## 11. Points sensibles du systeme

Les parties les plus sensibles sont :

- la logique d'authentification
- la correspondance entre `username` et `id_proprietaire`
- l'utilisation mixte CSV / SQLite
- la difference entre signaux bruts et signaux agreges

Si une autre IA ajoute des fonctionnalites, elle doit faire attention a ne pas casser :

- la redirection par role
- la generation automatique des comptes proprietaire
- l'analyse proprietaire par `OWNXXX`
- les pages admin / proprietaire

---

## 12. Fonctionnalites deja en place resumeees simplement

### Login

- connexion par compte
- redirection automatique vers l'interface du role

### Admin

- voir les entrepots
- gerer les comptes
- generer les comptes proprietaire
- consulter un resume par proprietaire

### Chercheur

- importer des donnees
- lancer des analyses logistiques
- travailler sur des recommandations

### Proprietaire

- voir ses entrepots
- voir ses historiques
- voir les deltas jour/nuit
- voir la fiabilite
- voir l'etat par saison
- voir un graphe saisonnier

### Moteur analytique

- traitement du signal
- analyse IoT
- scoring environnemental
- scoring global
- recommandation finale

---

## 13. Ce qu'une autre IA peut ajouter facilement

Extensions possibles relativement sures :

- meilleurs graphiques dans l'interface proprietaire
- badges couleur pour l'etat saisonnier
- exports PDF / CSV
- alertes automatiques
- gestion plus fine des proprietaires dans la base
- ajout d'un champ explicite `id_proprietaire` dans `utilisateurs`
- synchronisation complete entre CSV et SQLite
- historisation des actions admin
- interface plus riche pour les chercheurs

---

## 14. Fichiers a lire en priorite si une autre IA veut modifier le systeme

Ordre conseille :

1. `app.py`
2. `core/auth.py`
3. `pages/2_Dashboard_Admin.py`
4. `pages/4_Interface_Proprietaire.py`
5. `core/proprietaire_analysis.py`
6. `core/scoring.py`
7. `core/iot_analysis.py`
8. `core/warehouse_search.py`
9. `database/init_db.py`

---

## 15. Resume final

OptiStock Solutions est un systeme de supervision et d'analyse d'entrepots base sur :

- l'authentification par role
- les donnees entrepots
- les historiques IoT
- l'analyse de temperature et d'humidite
- des scores et recommandations

L'admin gere les comptes et supervise les donnees.
Le chercheur analyse et explore.
Le proprietaire consulte les informations importantes de ses entrepots.

Le coeur analytique du systeme repose sur :

- `core/scoring.py`
- `core/iot_analysis.py`
- `core/warehouse_search.py`
- `core/proprietaire_analysis.py`

Une autre IA peut ajouter des fonctionnalites, mais doit faire attention a :

- la correspondance compte <-> proprietaire
- les differences entre mesures brutes et agregats
- le fait que les donnees viennent encore a la fois de CSV et de SQLite
