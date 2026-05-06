# 📋 Rapport d'Audit Technique : OptiStock

## 1. Points d'Amélioration Majeurs & Suggestions Logiques

### 🛠️ Architecture & Découplage (Violation du SRP)
Le fichier `core/auth.py` est actuellement un "God Object". Il contient non seulement l'authentification, mais aussi la gestion des entrepôts et l'import de données IoT. 
*   **Suggestion :** Appliquer le **Single Responsibility Principle (SRP)** en éclatant `auth.py` en services distincts (`auth_service.py`, `warehouse_service.py`, `iot_service.py`).
*   **Centralisation DB :** Plusieurs fonctions redéfinissent leur propre connexion SQLite (`_connect`) au lieu d'utiliser systématiquement le wrapper robuste défini dans `utils/db.py`.

### 🔒 Sécurité & Robustesse
*   **Hachage des mots de passe :** L'utilisation de `hashlib.sha256` sans sel (salt) ni itérations (pepper/work factor) est insuffisante contre les attaques par dictionnaire ou tables arc-en-ciel. 
    *   **Suggestion :** Migrer vers `bcrypt` ou `argon2`.
*   **Gestion des types :** Le dossier `models/` contient des fichiers vides. L'application manipule des dictionnaires ou des tuples bruts, ce qui rend le code fragile lors de l'accès aux données.
    *   **Suggestion :** Implémenter des classes `Pydantic` ou des `dataclasses` pour typer les entités (Entrepot, Utilisateur, LectureIoT).

### 🌐 Internationalisation (i18n)
On observe un mélange de noms de fichiers et de variables en français (`carte.py`, `entrepot.py`) et en anglais (`auth.py`, `scoring.py`).
*   **Suggestion :** Standardiser le code (variables, fichiers, commentaires techniques) en **Anglais** pour faciliter l'interopérabilité et la maintenance, tout en gardant l'interface utilisateur (Streamlit) en Français.

---

## 2. Analyse de l'Organisation des Fichiers

L'arborescence actuelle est encombrée par des scripts de maintenance et de multiples fichiers de documentation à la racine.

### Structure Recommandée (Target Architecture)

```text
optistock_solutions/
├── src/                    # Code source principal
│   ├── core/               # Logique métier pure (Scoring, Algorithmes)
│   ├── services/           # Services d'accès aux données (Auth, Warehouse, IoT)
│   ├── database/           # Schémas SQL et migrations
│   ├── models/             # Classes de données (Pydantic/Dataclasses)
│   ├── ui/                 # Composants et styles réutilisables
│   │   ├── components/
│   │   └── theme.css
│   └── utils/              # Helpers techniques (DB, Math, IO)
├── pages/                  # Pages Streamlit (Gardées à la racine pour Streamlit)
├── tests/                  # Tests unitaires et intégration (Pytest)
├── scripts/                # Scripts de génération/nettoyage de données
├── docs/                   # Documentation centralisée (Archivage des .md épars)
├── data/                   # Fichiers statiques et CSV
├── requirements.txt
└── README.md
```

---

## 3. Nettoyage : Identification des Éléments Obsolètes

### 🗑️ Fichiers à supprimer ou déplacer
1.  **Fichiers "Parasites" :**
    *   `=` : Fichier créé par erreur (probablement une faute de frappe dans le terminal). **À supprimer.**
    *   `optistock.sqbpro` : Fichier de projet SQLite Browser, inutile pour l'exécution. **À ignorer/supprimer.**
2.  **Scripts de maintenance (À déplacer dans `/scripts`) :**
    *   `clean_data.py`, `fix_timestamps.py`, `generate_iot_data.py`, `generate_test_data_test_1.py`.
3.  **Documentation redondante (À fusionner dans `/docs`) :**
    *   `AI_SYSTEM_CONTEXT.md`, `AI_SYSTEM_CONTEXT_FR_LONG.md`, `MES_MODIFICATIONS_A_REINTEGRER.md`. Ces fichiers pollulent la racine et créent une confusion sur la source de vérité.
4.  **Dossiers vides :**
    *   `models/*.py` : Soit les remplir avec des modèles réels, soit les supprimer si la logique reste procédurale.

---

## 🎯 Plan d'Action Immédiat (Next Steps)

1.  **Phase 1 (Cleanup) :** Créer les dossiers `scripts/` et `docs/` et y déplacer les fichiers identifiés. Supprimer le fichier `=`.
2.  **Phase 2 (Refactoring) :** Extraire la logique de gestion des entrepôts de `core/auth.py` vers un nouveau fichier `core/warehouse_service.py`.
3.  **Phase 3 (Standardisation) :** Harmoniser la numérotation dans `pages/` (actuellement, on a deux fichiers commençant par `6_`).
