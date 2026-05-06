# OptiStock Solutions - System Context For Another AI

## Goal

This project is a Streamlit application for warehouse analysis with 3 main user roles:

- `admin`
- `chercheur`
- `proprietaire`

The app combines:

- authentication and role-based access
- warehouse and owner data loaded from local CSV files and/or SQLite
- IoT analysis on temperature and humidity histories
- scoring and decision support

This file explains the current system so another AI can safely add new features.

---

## Main Entry Points

- `app.py`
  - Main login screen
  - Redirects authenticated users to the correct role page

- `pages/2_Dashboard_Admin.py`
  - Admin dashboard
  - Shows warehouses, account management, owner sensor summary

- `pages/3_Interface_Chercheur.py`
  - Research/analyst interface
  - Contains recommendation and logistics analysis modules

- `pages/4_Interface_Proprietaire.py`
  - Owner interface
  - Shows owner warehouses, seasonal state, day/night differences, data reliability, and histories

---

## Current Roles

### 1. Admin

Admin can:

- view warehouse list
- view owner-level sensor summary
- create, update, deactivate, delete accounts
- generate missing owner accounts from warehouse data

Admin does **not** currently inspect full IoT history in the admin dashboard.

### 2. Chercheur

Research user can:

- work with recommendation and logistics analysis
- upload datasets
- run analysis and recommendations

### 3. Proprietaire

Owner can:

- log in with an account linked to an `id_proprietaire`
- view only their warehouses
- see important summaries for each warehouse
- inspect seasonal state
- inspect day/night differences
- inspect missing values / out-of-range values / reliability
- view raw temperature and humidity histories

---

## Authentication System

Main file:

- `core/auth.py`

Key behavior:

- users are stored in SQLite table `utilisateurs`
- authentication uses hashed passwords with `hashlib.pbkdf2_hmac`
- session is stored in `st.session_state`
- role-based redirection is handled in `ROLE_DESTINATIONS`

Important functions:

- `authenticate_user(...)`
- `login_user(...)`
- `logout_user(...)`
- `require_authentication(...)`
- `render_auth_status(...)`
- `create_user(...)`
- `update_user(...)`
- `reset_user_password(...)`
- `delete_user(...)`
- `sync_proprietaire_users_from_data(...)`

### Owner account generation

Owner accounts are generated from warehouse data:

- warehouse file contains `id_proprietaire` like `OWN001`
- username is generated as lowercase: `own001`
- temporary password format is:

`own001@123`

The owner page converts `own001` back to `OWN001`.

---

## Data Sources

### 1. Warehouse and sensor files

Primary local data folder:

- `data/cleaned/`

Fallback:

- `data/samples/`

Important files:

- `data/cleaned/entrepots.csv`
- `data/cleaned/temperature_ENT001.csv`, etc.
- `data/cleaned/humidite_ENT001.csv`, etc.

Warehouse CSV currently contains at least:

- `id_proprietaire`
- `id_entrepot`
- `latitude`
- `longitude`

Temperature history files generally contain:

- `id`
- `id_entrepot`
- `datetime`
- `capteur1`
- `capteur2`
- `capteur3`

Humidity history files generally contain:

- `id`
- `id_entrepot`
- `id_proprietaire`
- `datetime`
- `capteur1`
- `capteur2`
- `capteur3`

### 2. SQLite database

Location:

- `database/optistock.db`

Main schema creation:

- `database/init_db.py`

Important tables:

- `entrepots`
- `temperature`
- `humidite`
- `utilisateurs`

In practice, some UI parts rely on CSV first, especially for owner-to-warehouse mapping.

---

## Core Business Modules

### `core/scoring.py`

Contains:

- signal preprocessing helpers
- environmental scoring
- seasonal standards
- SAW 60/40 global decision logic
- recommendation text generation

Important concepts:

- missing-value interpolation
- rolling smoothing
- multi-sensor aggregation
- seasonal thresholds
- score fusion:
  - `60% logistique`
  - `40% environnement`

### `core/iot_analysis.py`

Builds IoT analysis pipelines:

- load CSV
- preprocess sensor series
- compute descriptive stats
- detect anomalies
- compute monthly / seasonal anomaly summaries
- generate structured IoT report

### `core/warehouse_search.py`

Warehouse ranking / scoring logic:

- loads temperature and humidity files for a warehouse
- computes warehouse robustness score
- includes penalties for:
  - missing data
  - spatial inconsistency between sensors
  - instability
  - incidents
- supports multiple storage types:
  - `STANDARD`
  - `FROID`
  - `SEC`
  - `CLIMATISE`

### `core/proprietaire_analysis.py`

Created for owner-specific analysis.

It computes, for each owner warehouse:

- day vs night difference
- data reliability
- missing values
- out-of-range values
- seasonal state

Important functions:

- `load_entrepots_for_owner(...)`
- `load_sensor_history(...)`
- `compute_day_night_difference(...)`
- `compute_data_reliability(...)`
- `compute_season_state(...)`
- `analyze_owner_entrepot(...)`
- `analyze_owner(...)`

Important note:

There are 2 different ways metrics are computed:

1. `compute_data_reliability(...)`
- works on raw sensor columns
- counts each sensor cell individually
- can produce large counts

2. `compute_season_state(...)`
- works on the mean of available sensors per timestamp
- counts seasonal out-of-range points on aggregated values

This explains why top-level reliability metrics can differ from seasonal table values.

---

## Owner Interface Current Logic

File:

- `pages/4_Interface_Proprietaire.py`

Current owner page shows:

- owner identifier
- linked warehouses
- summary table per warehouse
- selected warehouse details
- day/night deltas
- missing and out-of-range counts
- reliability percentages
- seasonal state table
- seasonal comparison graph
- raw temperature and humidity history tables

The sidebar is hidden globally using CSS.

---

## Admin Interface Current Logic

File:

- `pages/2_Dashboard_Admin.py`

Current admin page shows:

- warehouse list
- total active accounts
- researcher count
- owner count
- owner sensor summary
- account table with `user_id`
- create/update/delete/reset-password actions

Admin can also generate owner accounts from `id_proprietaire` found in data files.

---

## Important Implementation Constraints

### 1. Owner mapping

Current owner account mapping is based on:

- username `own003`
- owner id `OWN003`

This mapping is simple and implicit.

If another AI changes owner identity logic, it must update:

- `core/auth.py`
- `core/proprietaire_analysis.py`
- `pages/4_Interface_Proprietaire.py`

### 2. Hidden sidebar

Sidebar is intentionally hidden with CSS in pages.

If a new feature depends on sidebar navigation, it may conflict with current UX.

### 3. CSV-first reality

Although SQLite exists, several features still depend on local CSVs.

If another AI adds features, it should first decide:

- keep CSV as main source
- or migrate fully toward SQLite

Mixing both without a clear source-of-truth can create inconsistencies.

---

## Suggested Safe Extensions

Good next features another AI could add safely:

- owner charts with better visual design
- seasonal badges with color coding
- search/filter in owner historical tables
- export to CSV/PDF for owner reports
- owner-specific alerts
- admin management of warehouse metadata
- explicit `id_proprietaire` field in user accounts instead of implicit username mapping
- synchronization command between CSV warehouse owners and SQLite users

---

## Suggested Files To Read First

If another AI needs to extend the system, these files should be read first:

- `app.py`
- `core/auth.py`
- `core/proprietaire_analysis.py`
- `core/scoring.py`
- `core/iot_analysis.py`
- `core/warehouse_search.py`
- `pages/2_Dashboard_Admin.py`
- `pages/4_Interface_Proprietaire.py`
- `database/init_db.py`

---

## Current Mental Model

The system is best understood as:

1. Login and role routing
2. Data loaded from local CSV and partially SQLite
3. Domain-specific analytics in `core/`
4. Streamlit pages exposing role-based views

The most sensitive parts are:

- account creation and role logic
- owner-to-warehouse linking
- differences between raw sensor metrics and aggregated seasonal metrics

If another AI adds features, it should preserve those assumptions unless explicitly refactoring them.
