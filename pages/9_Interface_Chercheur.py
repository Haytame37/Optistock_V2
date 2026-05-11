import sqlite3
import uuid

import numpy as np
from scipy.optimize import minimize

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from core.iot_filter import get_compliant_warehouses
from core.messaging import (
    REQUEST_ACCEPTED,
    REQUEST_PENDING,
    create_contact_request,
    ensure_messaging_schema,
    get_chat_messages,
    get_researcher_requests,
    send_chat_message,
)
from utils.ui import hide_sidebar
from utils.db import DB_PATH, load_sql_to_dataframe, execute_query
from utils.product_conditions import PRODUCT_CONDITIONS
import json

def save_search_history(researcher_id, product, volume, duration, results):
    try:
        results_json = json.dumps(results)
        query = """
            INSERT INTO search_history (researcher_id, product_name, volume, duration_days, results_json)
            VALUES (?, ?, ?, ?, ?)
        """
        execute_query(query, (researcher_id, product, volume, duration, results_json))
    except Exception:
        pass


def fermat_weber(points: np.ndarray) -> tuple:
    """
    Calcule le point optimal d'implantation d'un entrepôt en minimisant
    la somme des distances euclidiennes brutes vers tous les points de livraison
    (Point de Fermat-Weber / Médiane Géométrique).

    Arguments :
        points : np.ndarray de forme (N, 2) avec colonnes [latitude, longitude]

    Retourne :
        (lat_opt, lon_opt, avg_distance_km)
    """
    # Fonction objectif : somme des distances euclidiennes brutes (pas de poids)
    def objective(p):
        diffs = points - p  # (N, 2)
        return np.sum(np.sqrt((diffs ** 2).sum(axis=1)))

    # Point de départ : centroïde des points
    x0 = points.mean(axis=0)

    # Solveur L-BFGS-B (gère les longitudes négatives sans contraintes de positivité)
    result = minimize(objective, x0, method="L-BFGS-B")

    lat_opt, lon_opt = result.x

    # Distance moyenne réelle (haversine)
    R = 6371.0
    lat1_r = np.radians(points[:, 0])
    lon1_r = np.radians(points[:, 1])
    lat2_r = np.radians(lat_opt)
    lon2_r = np.radians(lon_opt)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon / 2) ** 2
    avg_dist_km = float(np.mean(2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))))

    return float(lat_opt), float(lon_opt), avg_dist_km


st.set_page_config(
    page_title="Interface Chercheur | OptiStock",
    page_icon="📦",
    layout="wide",
)
hide_sidebar()


if "logged_in" not in st.session_state or not st.session_state.get("logged_in"):
    st.warning("Acces refuse. Veuillez vous connecter d'abord.")
    st.switch_page("pages/1_Login.py")
    st.stop()

if st.session_state.get("role") not in ["researcher", "admin"]:
    st.error("Acces reserve aux chercheurs ou administrateurs.")
    st.stop()

ensure_messaging_schema()


researcher_id = st.session_state.get("user_id")
user_name = st.session_state.get("first_name") or st.session_state.get("user", {}).get("first_name") or "Chercheur"

if "researcher_view" not in st.session_state:
    st.session_state["researcher_view"] = "home"

if "researcher_last_search" not in st.session_state:
    st.session_state["researcher_last_search"] = None


def set_view(view_name: str) -> None:
    st.session_state["researcher_view"] = view_name


def load_my_warehouses(current_researcher_id: int) -> pd.DataFrame:
    return load_sql_to_dataframe(
        """
        SELECT id_entrepot, nom, adresse, latitude, longitude, NULL AS volume_m3
        FROM my_warehouse
        WHERE researcher_id = ?
        ORDER BY nom, id_entrepot
        """,
        (current_researcher_id,),
    )


def load_delivery_points(current_researcher_id: int) -> pd.DataFrame:
    return load_sql_to_dataframe(
        """
        SELECT request_id, name, latitude, longitude
        FROM delivery_points
        WHERE researcher_id = ?
        ORDER BY name, request_id
        """,
        (current_researcher_id,),
    )


def load_owner_responses(current_researcher_id: int) -> pd.DataFrame:
    return load_sql_to_dataframe(
        """
        SELECT
            r.reservation_id,
            r.warehouse_id,
            w.name AS warehouse_name,
            w.address AS warehouse_address,
            r.global_score,
            r.status,
            r.reason,
            r.created_at,
            r.expires_at
        FROM reservations r
        LEFT JOIN warehouses w ON w.warehouse_id = r.warehouse_id
        WHERE r.researcher_id = ?
        ORDER BY datetime(r.created_at) DESC
        """,
        (current_researcher_id,),
    )


def load_researcher_discussions(current_researcher_id: int) -> pd.DataFrame:
    return get_researcher_requests(current_researcher_id)


def render_map(df_results: pd.DataFrame, df_my_warehouses: pd.DataFrame, df_clients: pd.DataFrame) -> None:
    all_lats, all_lons = [], []
    
    # Process results (Green)
    df_res = pd.DataFrame()
    if not df_results.empty:
        df_res = df_results.copy()
        df_res['latitude'] = pd.to_numeric(df_res['latitude'], errors='coerce')
        df_res['longitude'] = pd.to_numeric(df_res['longitude'], errors='coerce')
        df_res = df_res.dropna(subset=['latitude', 'longitude'])
        if not df_res.empty:
            all_lats.extend(df_res['latitude'].tolist())
            all_lons.extend(df_res['longitude'].tolist())
            
    # Process my warehouses (Red)
    df_my = pd.DataFrame()
    if not df_my_warehouses.empty:
        df_my = df_my_warehouses.copy()
        df_my['latitude'] = pd.to_numeric(df_my['latitude'], errors='coerce')
        df_my['longitude'] = pd.to_numeric(df_my['longitude'], errors='coerce')
        df_my = df_my.dropna(subset=['latitude', 'longitude'])
        if not df_my.empty:
            all_lats.extend(df_my['latitude'].tolist())
            all_lons.extend(df_my['longitude'].tolist())

    # Process clients (Blue)
    df_c = pd.DataFrame()
    if not df_clients.empty:
        df_c = df_clients.copy()
        df_c['latitude'] = pd.to_numeric(df_c['latitude'], errors='coerce')
        df_c['longitude'] = pd.to_numeric(df_c['longitude'], errors='coerce')
        df_c = df_c.dropna(subset=['latitude', 'longitude'])
        if not df_c.empty:
            all_lats.extend(df_c['latitude'].tolist())
            all_lons.extend(df_c['longitude'].tolist())

    if not all_lats:
        return
        
    center_lat = sum(all_lats) / len(all_lats) if all_lats else 31.7917
    center_lon = sum(all_lons) / len(all_lons) if all_lons else -7.0926

    m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

    # Clients (Bleu) - Tracé en premier pour être au fond
    if not df_c.empty:
        for _, row in df_c.iterrows():
            name = str(row.get('name', 'Client'))
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=name,
                tooltip=name,
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(m)

    # Entrepôts importés (Rouge) - Tracé en deuxième
    if not df_my.empty:
        for _, row in df_my.iterrows():
            nom = str(row.get('nom', 'Mon Entrepôt'))
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=nom,
                tooltip=nom,
                icon=folium.Icon(color="red", icon="building", prefix="fa")
            ).add_to(m)

    # Entrepôts résultats (Vert) - Tracé en dernier pour être au-dessus
    if not df_res.empty:
        for _, row in df_res.iterrows():
            nom = str(row.get('nom', 'Entrepôt (Résultat)'))
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=nom,
                tooltip=nom,
                icon=folium.Icon(color="green", icon="check", prefix="fa")
            ).add_to(m)

    st.markdown("#### Carte du Réseau Logistique")
    st.markdown(
        "<div style='display: flex; gap: 15px; margin-bottom: 10px; font-size: 14px; flex-wrap: wrap;'>"
        "<div style='display: flex; align-items: center; gap: 5px;'><div style='width: 12px; height: 12px; background-color: #5cb85c; border-radius: 50%;'></div> Résultats d'Analyse (Vert)</div>"
        "<div style='display: flex; align-items: center; gap: 5px;'><div style='width: 12px; height: 12px; background-color: #d9534f; border-radius: 50%;'></div> Mes Entrepôts Importés (Rouge)</div>"
        "<div style='display: flex; align-items: center; gap: 5px;'><div style='width: 12px; height: 12px; background-color: #337ab7; border-radius: 50%;'></div> Clients / Destinations (Bleu)</div>"
        "</div>",
        unsafe_allow_html=True
    )
    
    st_folium(m, width=1200, height=500, returned_objects=[])


def render_contact_owner_section(df_results: pd.DataFrame, product_name: str, current_researcher_id: int) -> None:
    st.write("")
    st.markdown("### Contacter un proprietaire")
    for _, row in df_results.iterrows():
        owner_id = row.get("owner_id")
        warehouse_id = row.get("id")
        warehouse_name = row.get("nom", warehouse_id)
        if pd.isna(owner_id) or warehouse_id is None:
            continue

        with st.container(border=True):
            st.markdown(
                f"**{warehouse_name}**  \n"
                f"Score logistique: `{row.get('score_logistique', 'n/a')}`"
            )
            default_message = (
                f"Bonjour, je souhaite echanger a propos de l'entrepot {warehouse_name} "
                f"pour le produit {product_name}."
            )
            request_message = st.text_area(
                "Message au proprietaire",
                value=default_message,
                key=f"discussion_message_{warehouse_id}_{product_name}",
                height=90,
            )
            if st.button(
                "Demander a parler au proprietaire",
                key=f"ask_owner_{warehouse_id}_{product_name}",
                use_container_width=True,
            ):
                ok, payload = create_contact_request(
                    warehouse_id=warehouse_id,
                    owner_id=int(owner_id),
                    researcher_id=current_researcher_id,
                    product_name=product_name,
                    message=request_message,
                )
                if ok:
                    st.success("Demande envoyee au proprietaire.")
                    st.rerun()
                else:
                    st.warning(payload)


def save_delivery_points(current_researcher_id: int, livraison_file) -> int:
    if livraison_file is None:
        return 0

    livraison_file.seek(0)
    df_livraison = pd.read_csv(livraison_file)
    if df_livraison.empty:
        return 0

    df_livraison.columns = [c.strip().lower() for c in df_livraison.columns]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    saved_points = 0

    for _, row in df_livraison.iterrows():
        name = row.get("name", row.get("nom", row.get("point", "Point inconnu")))
        lat = row.get("latitude", row.get("lat", 0.0))
        lon = row.get("longitude", row.get("lon", 0.0))

        cursor.execute(
            """
            INSERT INTO delivery_points (request_id, researcher_id, name, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4())[:8], current_researcher_id, name, lat, lon),
        )
        saved_points += 1

    conn.commit()
    conn.close()
    return saved_points


def save_my_warehouses(current_researcher_id: int, entrepot_file) -> int:
    if entrepot_file is None:
        return 0

    entrepot_file.seek(0)
    df_entrepot = pd.read_csv(entrepot_file)
    if df_entrepot.empty:
        return 0

    df_entrepot.columns = [c.strip().lower() for c in df_entrepot.columns]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    saved_warehouses = 0

    for _, row in df_entrepot.iterrows():
        w_id = row.get("id_entrepot", row.get("id", str(uuid.uuid4())[:8]))
        w_nom = row.get("name", row.get("nom", row.get("entrepot", "Entrepot importe")))
        w_adr = row.get("adresse", row.get("address", "Inconnue"))
        w_lat = row.get("latitude", row.get("lat", 0.0))
        w_lon = row.get("longitude", row.get("lon", 0.0))

        cursor.execute(
            """
            INSERT OR REPLACE INTO my_warehouse (id_entrepot, researcher_id, nom, adresse, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (w_id, current_researcher_id, w_nom, w_adr, w_lat, w_lon),
        )
        saved_warehouses += 1

    conn.commit()
    conn.close()
    return saved_warehouses


def sync_delivery_points(current_researcher_id: int, delivery_points: list[dict]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM delivery_points WHERE researcher_id = ?", (current_researcher_id,))

    for point in delivery_points:
        cursor.execute(
            """
            INSERT INTO delivery_points (request_id, researcher_id, name, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4())[:8],
                current_researcher_id,
                point["name"],
                point["latitude"],
                point["longitude"],
            ),
        )

    conn.commit()
    conn.close()
    return len(delivery_points)


def sync_my_warehouses(current_researcher_id: int, warehouses: list[dict]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM my_warehouse WHERE researcher_id = ?", (current_researcher_id,))

    for warehouse in warehouses:
        cursor.execute(
            """
            INSERT INTO my_warehouse (id_entrepot, researcher_id, nom, adresse, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                warehouse["id_entrepot"],
                current_researcher_id,
                warehouse["nom"],
                warehouse["adresse"],
                warehouse["latitude"],
                warehouse["longitude"],
            ),
        )

    conn.commit()
    conn.close()
    return len(warehouses)


st.markdown(
    """
<style>
body {
    font-family: "Segoe UI", sans-serif;
}
.hero {
    padding: 24px 28px;
    border-radius: 24px;
    background:
        radial-gradient(circle at top right, rgba(14,165,233,0.18), transparent 28%),
        linear-gradient(135deg, #0f172a 0%, #123a63 52%, #e0f2fe 160%);
    color: white;
    margin-bottom: 18px;
}
.hero h1 {
    margin: 0 0 8px 0;
    font-size: 32px;
}
.hero p {
    margin: 0;
    max-width: 760px;
    color: rgba(255,255,255,0.84);
}
.nav-card {
    background: white;
    border: 1px solid #dbe4ee;
    border-radius: 20px;
    padding: 22px;
    min-height: 190px;
    box-shadow: 0 14px 34px rgba(15, 23, 42, 0.05);
}
.nav-card h3 {
    margin-top: 0;
    color: #0f3c68;
}
.nav-card p {
    color: #475569;
    font-size: 14px;
}
.kpi-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    border: 1px solid #d8e6f2;
    border-radius: 18px;
    padding: 18px;
}
.kpi-label {
    color: #64748b;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.kpi-value {
    color: #0f172a;
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}
.section-card {
    background: white;
    border: 1px solid #dbe4ee;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 18px;
}
.subtle {
    color: #64748b;
    font-size: 14px;
}
.wizard-shell {
    background: #f6f7fb;
    border: 1px solid #e5e7eb;
    border-radius: 24px;
    padding: 18px;
}
.wizard-card {
    background: white;
    border: 1px solid #d6dae3;
    border-radius: 18px;
    padding: 20px;
    margin-top: 18px;
}
.wizard-title {
    font-size: 28px;
    font-weight: 800;
    color: #111827;
}
.wizard-subtitle {
    color: #6b7280;
    font-size: 14px;
}
.mini-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    height: 24px;
    padding: 0 8px;
    border-radius: 999px;
    background: #dbeafe;
    color: #1d4ed8;
    font-size: 12px;
    font-weight: 700;
}
.list-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 18px;
    padding: 16px 0;
    border-top: 1px solid #edf0f5;
}
.list-item:first-child {
    border-top: none;
}
.list-name {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
}
.list-meta {
    font-size: 13px;
    color: #6b7280;
    margin-top: 4px;
}
.step-label {
    text-align: center;
    font-size: 13px;
    color: #6b7280;
    margin-top: 8px;
}
.chat-bubble {
    border: 1px solid #dbe4ee;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 10px;
    background: #f8fbff;
}
.chat-meta {
    font-size: 12px;
    color: #64748b;
    margin-bottom: 6px;
}
</style>
""",
    unsafe_allow_html=True,
)


my_warehouses_df = load_my_warehouses(researcher_id)
delivery_points_df = load_delivery_points(researcher_id)
owner_responses_df = load_owner_responses(researcher_id)
researcher_discussions_df = load_researcher_discussions(researcher_id)

if "researcher_search_step" not in st.session_state:
    st.session_state["researcher_search_step"] = 1

if "researcher_search_started" not in st.session_state:
    st.session_state["researcher_search_started"] = False

if "researcher_search_warehouses" not in st.session_state:
    st.session_state["researcher_search_warehouses"] = [
        {
            "id_entrepot": row["id_entrepot"],
            "nom": row["nom"],
            "adresse": row["adresse"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "volume_m3": float(row["volume_m3"]) if pd.notna(row["volume_m3"]) else 0.0,
        }
        for _, row in my_warehouses_df.iterrows()
    ]

if "researcher_search_clients" not in st.session_state:
    st.session_state["researcher_search_clients"] = [
        {
            "name": row["name"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
        }
        for _, row in delivery_points_df.iterrows()
    ]

if "researcher_search_product" not in st.session_state:
    st.session_state["researcher_search_product"] = list(PRODUCT_CONDITIONS.keys())[0]

if "researcher_search_volume" not in st.session_state:
    st.session_state["researcher_search_volume"] = 0.0

if "researcher_search_duration" not in st.session_state:
    st.session_state["researcher_search_duration"] = 7

if "researcher_quick_search" not in st.session_state:
    st.session_state["researcher_quick_search"] = False

# Récupération de l'état des résultats (Session ou Historique DB)
results_snapshot = st.session_state.get("researcher_last_search")

if not results_snapshot:
    # Essayer de charger la toute dernière recherche depuis la base de données
    try:
        history_df = load_sql_to_dataframe(
            "SELECT product_name, volume, duration_days, results_json FROM search_history WHERE researcher_id = ? ORDER BY created_at DESC LIMIT 1",
            (researcher_id,)
        )
        if not history_df.empty:
            last_row = history_df.iloc[0]
            results_snapshot = {
                "product": last_row["product_name"],
                "volume": last_row["volume"],
                "duration_days": last_row["duration_days"],
                "results": json.loads(last_row["results_json"])
            }
    except Exception:
        pass

results_count = len(results_snapshot["results"]) if results_snapshot else 0

current_view = st.session_state["researcher_view"]

st.markdown(
    f"""
<div class="hero">
    <h1>Interface chercheur</h1>
    <p>
        Bonjour {user_name}. Cette interface vous permet de lancer une recherche d'entrepot,
        consulter les resultats de vos analyses et suivre les retours associes aux proprietaires.
    </p>
</div>
""",
    unsafe_allow_html=True,
)

if current_view == "home":
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(
            f"""
<div class="kpi-card">
    <div class="kpi-label">Entrepots importes</div>
    <div class="kpi-value">{len(my_warehouses_df)}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with kpi2:
        st.markdown(
            f"""
<div class="kpi-card">
    <div class="kpi-label">Points de livraison</div>
    <div class="kpi-value">{len(delivery_points_df)}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with kpi3:
        st.markdown(
            f"""
<div class="kpi-card">
    <div class="kpi-label">Reponses / statuts recus</div>
    <div class="kpi-value">{len(owner_responses_df)}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.write("")

    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        with st.container(border=True):
            st.markdown('<h3 style="margin-top:0;">Recherche d\'entrepot</h3>', unsafe_allow_html=True)
            st.markdown("Acceder a l'interface actuelle de recherche, importer les donnees et lancer l'analyse logistique.\n\n*Utilise le moteur deja present dans l'application.*")
            if st.button("Ouvrir la recherche", use_container_width=True):
                st.session_state["researcher_search_started"] = True
                st.session_state["researcher_search_step"] = 1
                set_view("search")

    with nav2:
        with st.container(border=True):
            st.markdown('<h3 style="margin-top:0; color:#27ae60;">Mes entrepôts</h3>', unsafe_allow_html=True)
            st.markdown("Consulter la liste de vos entrepôts loués et surveillez en temps réel les conditions IoT.\n\n*Réservations confirmées uniquement.*")
            if st.button("Voir mes entrepôts", use_container_width=True):
                set_view("mes_entrepots")

    with nav3:
        with st.container(border=True):
            st.markdown('<h3 style="margin-top:0;">Reponses des proprietaires</h3>', unsafe_allow_html=True)
            st.markdown("Suivre les statuts de reservation et les retours disponibles sur les entrepots contactes.\n\n*Vue branchee sur les reservations deja stockees.*")
            if st.button("Voir les reponses", use_container_width=True):
                set_view("responses")

if current_view != "home":
    top_left, top_right = st.columns([8, 2])
    with top_left:
        labels = {
            "search": "Recherche d'entrepot",
            "mes_entrepots": "Mes entrepôts loués",
            "responses": "Reponses des proprietaires",
            "results": "Mes resultats"
        }
        st.subheader(labels.get(current_view, "Interface chercheur"))
    with top_right:
        if st.button("Retour a l'accueil", use_container_width=True):
            set_view("home")
            st.rerun()


if current_view == "search":
    tab1, tab2 = st.tabs(["Module 1: Trouver un entrepôt", "Module 2: Implanter un nouvel entrepôt"])
    with tab2:
        # ── Session state pour Module 2 ────────────────────────────────────
        if "m2_clients" not in st.session_state:
            st.session_state["m2_clients"] = []
        if "m2_last_file" not in st.session_state:
            st.session_state["m2_last_file"] = None

        m2_clients = st.session_state["m2_clients"]

        # ── Saisie des points de livraison ─────────────────────────────────
        with st.container(border=True):
            st.markdown("### Points de livraison (Clients)")

            # Formulaire manuel
            with st.expander("➕ Ajouter un client manuellement", expanded=False):
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    m2_name = st.text_input("Nom du client", key="m2_name")
                with mc2:
                    m2_lat = st.number_input("Latitude", value=33.5731, format="%.4f", key="m2_lat")
                with mc3:
                    m2_lon = st.number_input("Longitude", value=-7.5898, format="%.4f", key="m2_lon")
                if st.button("Ajouter", key="m2_add_client"):
                    if m2_name.strip():
                        st.session_state["m2_clients"].append(
                            {"name": m2_name.strip(), "latitude": m2_lat, "longitude": m2_lon}
                        )
                        st.rerun()
                    else:
                        st.warning("Veuillez saisir un nom de client.")

            # Import CSV
            st.markdown("**Ou importer via un fichier CSV** (colonnes : nom, latitude, longitude)")
            m2_file = st.file_uploader("Fichier CSV", type=["csv"], key="m2_csv_uploader")
            if m2_file is not None:
                file_id = f"{m2_file.name}_{m2_file.size}"
                if st.session_state.get("m2_last_file") != file_id:
                    try:
                        df_m2 = pd.read_csv(m2_file)
                        df_m2.columns = [str(c).strip().lower() for c in df_m2.columns]
                        col_nom = next((c for c in df_m2.columns if c in ["nom", "name", "client"]), None)
                        col_lat = next((c for c in df_m2.columns if "lat" in c), None)
                        col_lon = next((c for c in df_m2.columns if "lon" in c), None)
                        if col_nom and col_lat and col_lon:
                            count = 0
                            for _, row in df_m2.iterrows():
                                n = str(row[col_nom]).strip()
                                if pd.isna(row[col_lat]) or pd.isna(row[col_lon]) or not n or n == "nan":
                                    continue
                                st.session_state["m2_clients"].append(
                                    {"name": n, "latitude": float(row[col_lat]), "longitude": float(row[col_lon])}
                                )
                                count += 1
                            if count > 0:
                                st.session_state["m2_last_file"] = file_id
                                st.success(f"✅ {count} clients importés.")
                                st.rerun()
                        else:
                            st.error("Colonnes requises : nom, latitude, longitude.")
                    except Exception as e:
                        st.error(f"Erreur de lecture : {e}")

        # ── Liste des clients saisis ────────────────────────────────────────
        with st.container(border=True):
            h_col1, h_col2 = st.columns([7, 3])
            with h_col1:
                st.markdown(
                    f'### Mes clients <span class="mini-badge">{len(m2_clients)}</span>',
                    unsafe_allow_html=True
                )
            with h_col2:
                if m2_clients:
                    if st.button("🗑️ Tout supprimer", key="m2_clear_all", use_container_width=True):
                        st.session_state["m2_clients"] = []
                        st.rerun()

            if not m2_clients:
                st.info("Ajoutez au moins 2 clients pour calculer un point d'implantation.")
            else:
                for idx, client in enumerate(m2_clients):
                    ci1, ci2 = st.columns([8, 2])
                    with ci1:
                        st.markdown(
                            f"""<div class="list-item">
                                <div class="list-name">{client['name']}</div>
                                <div class="list-meta">{client['latitude']:.4f}N · {client['longitude']:.4f}E</div>
                            </div>""",
                            unsafe_allow_html=True
                        )
                    with ci2:
                        if st.button("Suppr.", key=f"m2_del_{idx}", use_container_width=True):
                            st.session_state["m2_clients"].pop(idx)
                            st.rerun()

        # ── Calcul Fermat-Weber ─────────────────────────────────────────────
        if len(m2_clients) >= 2:
            if st.button("🔍 Calculer le point optimal d'implantation", key="m2_run", type="primary", use_container_width=True):
                pts = np.array([[c["latitude"], c["longitude"]] for c in m2_clients])
                with st.spinner("Calcul en cours (méthode Fermat-Weber, solveur L-BFGS-B)..."):
                    lat_opt, lon_opt, avg_dist = fermat_weber(pts)
                st.session_state["m2_result"] = {"lat": lat_opt, "lon": lon_opt, "avg_dist": avg_dist}

        # ── Affichage des résultats ────────────────────────────────────────
        if "m2_result" in st.session_state and m2_clients:
            res = st.session_state["m2_result"]

            st.divider()
            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("Latitude optimale", f"{res['lat']:.4f}°")
            with r2:
                st.metric("Longitude optimale", f"{res['lon']:.4f}°")
            with r3:
                st.metric("Distance moyenne (km)", f"{res['avg_dist']:.2f} km")

            # Carte Folium
            all_lats = [c["latitude"] for c in m2_clients] + [res["lat"]]
            all_lons = [c["longitude"] for c in m2_clients] + [res["lon"]]
            center_lat = sum(all_lats) / len(all_lats)
            center_lon = sum(all_lons) / len(all_lons)

            m2_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)

            # Points de livraison (Bleu)
            for client in m2_clients:
                folium.Marker(
                    location=[client["latitude"], client["longitude"]],
                    popup=client["name"],
                    tooltip=client["name"],
                    icon=folium.Icon(color="blue", icon="user", prefix="fa")
                ).add_to(m2_map)

            # Point optimal (Vert, plus grand, pulsant)
            folium.Marker(
                location=[res["lat"], res["lon"]],
                popup=f"Point optimal : ({res['lat']:.4f}, {res['lon']:.4f})",
                tooltip=f"📍 Implantation optimale — dist. moy. {res['avg_dist']:.2f} km",
                icon=folium.Icon(color="green", icon="home", prefix="fa")
            ).add_to(m2_map)

            # Lignes de connexion (clients → point optimal)
            for client in m2_clients:
                folium.PolyLine(
                    locations=[[client["latitude"], client["longitude"]], [res["lat"], res["lon"]]],
                    color="gray",
                    weight=1.5,
                    opacity=0.6,
                    dash_array="5"
                ).add_to(m2_map)

            st.markdown("#### Carte du Point d'Implantation Optimal")
            st.markdown(
                "<div style='display:flex;gap:15px;margin-bottom:10px;font-size:14px;flex-wrap:wrap;'>"
                "<div style='display:flex;align-items:center;gap:5px;'><div style='width:12px;height:12px;background-color:#5cb85c;border-radius:50%;'></div> Point d'implantation optimal (Vert)</div>"
                "<div style='display:flex;align-items:center;gap:5px;'><div style='width:12px;height:12px;background-color:#337ab7;border-radius:50%;'></div> Clients / Destinations (Bleu)</div>"
                "</div>",
                unsafe_allow_html=True
            )
            st_folium(m2_map, width=1200, height=500, returned_objects=[])
    with tab1:
        current_step = st.session_state["researcher_search_step"]
        draft_warehouses = st.session_state["researcher_search_warehouses"]
        draft_clients = st.session_state["researcher_search_clients"]

        st.markdown('<div class="wizard-shell">', unsafe_allow_html=True)
        step_cols = st.columns(4)
        step_labels = ["Produit", "Entrepots", "Clients", "Resultats"]
        for idx, label in enumerate(step_labels, start=1):
            with step_cols[idx - 1]:
                if st.button(
                    f"{idx:02d}\n{label}",
                    key=f"wizard_step_{idx}",
                    use_container_width=True,
                    type="primary" if current_step == idx else "secondary",
                ):
                    st.session_state["researcher_search_step"] = idx
                    st.rerun()
                # Label supprimé ici car répété dans le titre de la section

        if current_step == 1:
            with st.container(border=True):
                st.markdown("### Parametres produit")
                c1, c2 = st.columns(2)
                with c1:
                    st.session_state["researcher_search_product"] = st.selectbox(
                        "Produit",
                        options=list(PRODUCT_CONDITIONS.keys()),
                        index=list(PRODUCT_CONDITIONS.keys()).index(st.session_state["researcher_search_product"]),
                    )
                with c2:
                    st.session_state["researcher_search_volume"] = st.number_input(
                        "Volume total (m3)",
                        min_value=0.0,
                        step=0.1,
                        value=float(st.session_state["researcher_search_volume"]),
                    )

                st.session_state["researcher_search_duration"] = st.number_input(
                    "Duree de stockage estimee (jours)",
                    min_value=1,
                    max_value=365,
                    value=int(st.session_state["researcher_search_duration"]),
                )

                st.divider()
                col_next, col_quick = st.columns(2)
                with col_next:
                    if st.button("Suivant — Entrepots ->", key="go_to_warehouses_first", use_container_width=True):
                        st.session_state["researcher_quick_search"] = False
                        st.session_state["researcher_search_step"] = 2
                        st.rerun()
                with col_quick:
                    if st.button("🚀 Recherche rapide (produit uniquement)", key="go_quick_search", use_container_width=True, type="primary"):
                        st.session_state["researcher_quick_search"] = True
                        st.session_state["researcher_search_step"] = 4
                        st.rerun()
                    st.markdown(
                        '<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:10px 14px;font-size:13px;color:#1e40af;">'
                        "<b>Mode rapide</b> : chercher parmi tous les entrepots de la plateforme "
                        "sans entrer d'entrepots ou de clients."
                        "</div>",
                        unsafe_allow_html=True,
                    )

            # Fin de l'étape 1

        elif current_step == 2:
            with st.container(border=True):
                st.markdown("### Ajouter un entrepot existant")

                c1, c2 = st.columns(2)
                with c1:
                    warehouse_name = st.text_input("Nom", key="draft_wh_name", placeholder="Entrepot Nord Casablanca")
                with c2:
                    warehouse_address = st.text_input("Adresse / Ville", key="draft_wh_address", placeholder="Ain Sebaa, Casablanca")

                c3, c4, c5 = st.columns(3)
                with c3:
                    warehouse_lat = st.number_input("Latitude", key="draft_wh_lat", format="%.4f", value=33.57)
                with c4:
                    warehouse_lon = st.number_input("Longitude", key="draft_wh_lon", format="%.4f", value=-7.59)
                with c5:
                    warehouse_volume = st.number_input("Volume (m3)", key="draft_wh_volume", min_value=0.0, value=5000.0, step=100.0)

                if st.button("+ Ajouter", key="add_draft_warehouse"):
                    if warehouse_name.strip() and warehouse_address.strip():
                        draft_warehouses.append(
                            {
                                "id_entrepot": str(uuid.uuid4())[:8].upper(),
                                "nom": warehouse_name.strip(),
                                "adresse": warehouse_address.strip(),
                                "latitude": float(warehouse_lat),
                                "longitude": float(warehouse_lon),
                                "volume_m3": float(warehouse_volume),
                            }
                        )
                        st.session_state["researcher_search_warehouses"] = draft_warehouses
                        st.rerun()
                    else:
                        st.warning("Le nom et l'adresse sont requis pour ajouter un entrepot.")

            # Wizard card closing handled by container


            with st.container(border=True):
                st.markdown(
                    f'### Mes entrepots <span class="mini-badge">{len(draft_warehouses)}</span>',
                    unsafe_allow_html=True,
                )
                if not draft_warehouses:
                    st.info("Ajoute au moins un entrepot pour continuer.")
                else:
                    for idx, warehouse in enumerate(draft_warehouses):
                        info_col, action_col = st.columns([8, 2])
                        with info_col:
                            st.markdown(
                                f"""
        <div class="list-item">
            <div>
                <div class="list-name">{warehouse["nom"]}</div>
                <div class="list-meta">{warehouse["adresse"]} · {warehouse["latitude"]:.2f}N · {warehouse["longitude"]:.2f}E · {warehouse["volume_m3"]:.0f} m3</div>
            </div>
        </div>
        """,
                                unsafe_allow_html=True,
                            )
                        with action_col:
                            if st.button("Suppr.", key=f"remove_wh_{idx}", use_container_width=True):
                                draft_warehouses.pop(idx)
                                st.session_state["researcher_search_warehouses"] = draft_warehouses
                                st.rerun()
                prev_col, next_col, skip_col = st.columns(3)
                with prev_col:
                    if st.button("<- Precedent", key="back_to_product_first", use_container_width=True):
                        st.session_state["researcher_search_step"] = 1
                        st.rerun()
                with next_col:
                    if st.button("Suivant — Clients ->", key="go_to_clients", use_container_width=True):
                        st.session_state["researcher_quick_search"] = False
                        st.session_state["researcher_search_step"] = 3
                        st.rerun()
                with skip_col:
                    if st.button("Passer aux Resultats ->", key="skip_to_results_from_wh", use_container_width=True):
                        st.session_state["researcher_quick_search"] = False
                        st.session_state["researcher_search_step"] = 4
                        st.rerun()
            # Division fermée par le contexte du conteneur


        elif current_step == 3:
            with st.container(border=True):
                st.markdown("### Ajouter un client / point de livraison")
                c1, c2, c3 = st.columns(3)
                with c1:
                    client_name = st.text_input("Nom du client", key="draft_client_name", placeholder="Client Beni Mellal")
                with c2:
                    client_lat = st.number_input("Latitude client", key="draft_client_lat", format="%.4f", value=32.6667)
                with c3:
                    client_lon = st.number_input("Longitude client", key="draft_client_lon", format="%.4f", value=-6.35)

                if st.button("+ Ajouter client", key="add_draft_client"):
                    if client_name.strip():
                        draft_clients.append(
                            {
                                "name": client_name.strip(),
                                "latitude": float(client_lat),
                                "longitude": float(client_lon),
                            }
                        )
                        st.session_state["researcher_search_clients"] = draft_clients
                        st.rerun()
                    else:
                        st.warning("Le nom du client est requis.")

                st.markdown("---")
                st.markdown("**Ou importer une liste depuis un fichier CSV :**")
                st.caption("Le fichier CSV doit contenir les colonnes : `nom` (ou `name`), `latitude` (ou `lat`), `longitude` (ou `lon`).")
                uploaded_file = st.file_uploader("Fichier CSV", type=["csv"], key="csv_clients_uploader")
                if uploaded_file is not None:
                    # Éviter de ré-importer le même fichier en boucle
                    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
                    if st.session_state.get("last_imported_client_file") != file_id:
                        try:
                            df_clients = pd.read_csv(uploaded_file)
                        
                            # Normaliser les noms de colonnes
                            df_clients.columns = [str(col).strip().lower() for col in df_clients.columns]
                        
                            # Chercher les colonnes correspondantes
                            col_nom = next((col for col in df_clients.columns if col in ['nom', 'name', 'client', 'nom du client', 'nom_du_client']), None)
                            col_lat = next((col for col in df_clients.columns if 'lat' in col), None)
                            col_lon = next((col for col in df_clients.columns if 'lon' in col), None)

                            if col_nom and col_lat and col_lon:
                                added_count = 0
                                for _, row in df_clients.iterrows():
                                    # Nettoyage minimal pour éviter les NaN ou chaînes vides
                                    name_val = str(row[col_nom]).strip()
                                    if pd.isna(row[col_lat]) or pd.isna(row[col_lon]) or not name_val or name_val == "nan":
                                        continue
                                
                                    st.session_state["researcher_search_clients"].append(
                                        {
                                            "name": name_val,
                                            "latitude": float(row[col_lat]),
                                            "longitude": float(row[col_lon]),
                                        }
                                    )
                                    added_count += 1
                            
                                if added_count > 0:
                                    st.session_state["last_imported_client_file"] = file_id
                                    st.success(f"✅ {added_count} clients importés avec succès !")
                                    st.rerun()
                            else:
                                st.error("Le fichier CSV doit contenir les colonnes : nom, latitude, longitude. Colonnes trouvées : " + ", ".join(df_clients.columns))
                        except Exception as e:
                            st.error(f"Erreur lors de la lecture du fichier CSV : {e}")

            # Division fermée par le contexte du conteneur


            with st.container(border=True):
                header_col1, header_col2 = st.columns([7, 3])
                with header_col1:
                    st.markdown(
                        f'### Mes clients <span class="mini-badge">{len(draft_clients)}</span>',
                        unsafe_allow_html=True,
                    )
                with header_col2:
                    if draft_clients:
                        if st.button("🗑️ Tout supprimer", key="clear_all_clients", use_container_width=True):
                            try:
                                execute_query("DELETE FROM delivery_points WHERE researcher_id = ?", (researcher_id,))
                            except Exception:
                                pass
                            st.session_state["researcher_search_clients"] = []
                            st.rerun()
                if not draft_clients:
                    st.info("Ajoute au moins un client pour alimenter la partie logistique.")
                else:
                    for idx, client in enumerate(draft_clients):
                        info_col, action_col = st.columns([8, 2])
                        with info_col:
                            st.markdown(
                                f"""
        <div class="list-item">
            <div>
                <div class="list-name">{client["name"]}</div>
                <div class="list-meta">{client["latitude"]:.4f}, {client["longitude"]:.4f}</div>
            </div>
        </div>
        """,
                                unsafe_allow_html=True,
                            )
                        with action_col:
                            if st.button("Suppr.", key=f"remove_client_{idx}", use_container_width=True):
                                draft_clients.pop(idx)
                                st.session_state["researcher_search_clients"] = draft_clients
                                st.rerun()

                prev_col, next_col = st.columns(2)
                with prev_col:
                    if st.button("<- Precedent", key="back_to_warehouses", use_container_width=True):
                        st.session_state["researcher_search_step"] = 2
                        st.rerun()
                with next_col:
                    if st.button("Suivant — Resultats ->", key="go_to_results_step", use_container_width=True):
                        st.session_state["researcher_search_step"] = 4
                        st.rerun()
            # Division fermée par le contexte du conteneur


        elif current_step == 4:
            with st.container(border=True):
                st.markdown("### Lancer l'analyse")
            st.write(
                f"Produit : **{st.session_state['researcher_search_product']}** | "
                f"Entrepots saisis : **{len(draft_warehouses)}** | "
                f"Clients saisis : **{len(draft_clients)}**"
            )
            st.write(
                f"Volume : **{st.session_state['researcher_search_volume']:.1f} m3** | "
                f"Duree : **{st.session_state['researcher_search_duration']} jour(s)**"
            )

            launch_disabled = False
            is_quick = st.session_state.get("researcher_quick_search", False)

            if is_quick:
                st.info(
                    "🚀 **Mode recherche rapide** : la recherche va parcourir tous les entrepots "
                    "disponibles sur la plateforme et les classer par conformite au produit choisi. "
                    "Aucun entrepot ni point de livraison personnel n'est requis."
                )
            else:
                if not draft_warehouses and not draft_clients:
                    st.warning("Aucun entrepot ni client saisi. La recherche utilisera tous les entrepots de la plateforme.")
                elif not draft_warehouses:
                    st.warning("Aucun entrepot personnel saisi — la plateforme sera utilisee comme source.")
                elif not draft_clients:
                    st.info("Aucun point de livraison — le score sera base uniquement sur les conditions IoT.")

            prev_col, run_col = st.columns(2)
            with prev_col:
                back_step = 1 if is_quick else 3
                if st.button("<- Precedent", key="back_to_clients", use_container_width=True):
                    st.session_state["researcher_search_step"] = back_step
                    st.rerun()
            with run_col:
                run_search = st.button("Lancer l'analyse", key="run_search_new_ui", use_container_width=True, type="primary")

            if run_search:
                if draft_clients:
                    saved_points = sync_delivery_points(researcher_id, draft_clients)
                else:
                    saved_points = 0
                if draft_warehouses:
                    saved_warehouses = sync_my_warehouses(researcher_id, draft_warehouses)
                else:
                    saved_warehouses = 0

                with st.spinner("Analyse des historiques IoT en cours..."):
                    from core.logistique import classer_entrepots_logistique
                    compliant_warehouses = get_compliant_warehouses(
                        st.session_state["researcher_search_product"]
                    )
                    suggestions = classer_entrepots_logistique(compliant_warehouses, researcher_id)

                st.session_state["researcher_last_search"] = {
                    "product": st.session_state["researcher_search_product"],
                    "volume": st.session_state["researcher_search_volume"],
                    "duration_days": st.session_state["researcher_search_duration"],
                    "saved_points": saved_points,
                    "saved_warehouses": saved_warehouses,
                    "results": suggestions,
                }
            
                # Sauvegarde en base de données pour l'historique
                save_search_history(
                    researcher_id,
                    st.session_state["researcher_search_product"],
                    st.session_state["researcher_search_volume"],
                    st.session_state["researcher_search_duration"],
                    suggestions
                )

                st.success(
                    f"Analyse terminee. {saved_points} client(s) et {saved_warehouses} entrepot(s) ont ete enregistres."
                )

                if suggestions:
                    df_suggestions = pd.DataFrame(suggestions)
                    suggestion_columns = [
                        c
                        for c in [
                            "nom",
                            "score_logistique",
                            "distance_km",
                            "avg_temp",
                            "avg_hum",
                            "status",
                        ]
                        if c in df_suggestions.columns
                    ]
                    st.dataframe(
                        df_suggestions[suggestion_columns],
                        column_config={
                            "nom": "Nom de l'entrepot",
                            "score_logistique": st.column_config.NumberColumn("Score logistique", format="%.2f"),
                            "distance_km": st.column_config.NumberColumn("Distance (km)", format="%.2f"),
                            "avg_temp": st.column_config.NumberColumn("Temperature moyenne", format="%.1f C"),
                            "avg_hum": st.column_config.NumberColumn("Humidite moyenne", format="%.1f %%"),
                            "status": "Statut",
                        },
                        use_container_width=True,
                        hide_index=True,
                    )
                
                    # Render Map
                    current_clients_df = pd.DataFrame(st.session_state.get("researcher_search_clients", []))
                    current_my_warehouses_df = pd.DataFrame(st.session_state.get("researcher_search_warehouses", []))
                    render_map(df_suggestions, current_my_warehouses_df, current_clients_df)

                    render_contact_owner_section(
                        df_results=df_suggestions,
                        product_name=st.session_state["researcher_search_product"],
                        current_researcher_id=researcher_id,
                    )
                    if st.button("Ouvrir l'espace resultats", key="goto_results_from_wizard"):
                        set_view("results")
                        st.rerun()
                else:
                    st.warning("Aucun entrepot conforme n'a ete trouve pour cette recherche.")

            # Division fermée par le contexte du conteneur


        # Fin de la vue recherche



elif current_view == "mes_entrepots":
    st.markdown("### Vos Entrepôts Loués (Actifs)")
    st.write("Voici la liste des entrepôts pour lesquels vous avez une location en cours. Accédez au suivi IoT pour surveiller vos marchandises en temps réel.")
    
    rented_warehouses = owner_responses_df[owner_responses_df['status'] == 'confirmed']
    
    if rented_warehouses.empty:
        st.info("Vous n'avez aucun entrepôt loué pour le moment.")
    else:
        for idx, row in rented_warehouses.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([8, 2])
                with c1:
                    st.markdown(f"#### 📦 {row['warehouse_name']}")
                    st.markdown(f"📍 **Adresse:** {row['warehouse_address']}")
                    st.caption(f"Réservation confirmée le : {row['created_at']}")
                with c2:
                    st.write("")
                    if st.button("📊 Dashboard IoT", key=f"iot_{row['warehouse_id']}_{row.get('reservation_id', idx)}", type="primary", use_container_width=True):
                        st.switch_page("pages/8_Dashboard_IoT.py")
        
if current_view == "results":
    st.markdown('<div class="section-card"><h3 style="margin:0;">Historique des recherches</h3></div>', unsafe_allow_html=True)

    # Charger l'historique depuis la base de données
    history_df = load_sql_to_dataframe(
        "SELECT id, product_name, volume, duration_days, results_json, created_at FROM search_history WHERE researcher_id = ? ORDER BY created_at DESC",
        (researcher_id,)
    )

    if not history_df.empty:
        # Création d'un label lisible pour le sélecteur
        history_df['label'] = history_df.apply(
            lambda r: f"{r['created_at']} | {r['product_name']} | {r['volume']:.1f} m3", axis=1
        )
        
        selected_label = st.selectbox(
            "Consulter une analyse passée :",
            options=history_df['label'].tolist(),
            index=0
        )
        
        selected_row = history_df[history_df['label'] == selected_label].iloc[0]
        
        # Reconstitution du snapshot pour l'affichage
        results_snapshot = {
            "product": selected_row["product_name"],
            "volume": selected_row["volume"],
            "duration_days": selected_row["duration_days"],
            "results": json.loads(selected_row["results_json"])
        }

        st.divider()
        
        meta1, meta2, meta3, meta4 = st.columns(4)
        with meta1:
            st.metric("Produit", results_snapshot["product"])
        with meta2:
            st.metric("Volume", f'{results_snapshot["volume"]:.1f} m3')
        with meta3:
            st.metric("Durée", f'{results_snapshot["duration_days"]} jour(s)')
        with meta4:
            st.metric("Résultats trouvés", len(results_snapshot["results"]))

        st.write("")

        if results_snapshot["results"]:
            df_results = pd.DataFrame(results_snapshot["results"])
            preferred_columns = [
                c for c in [
                    "nom", "score_logistique", "distance_km", 
                    "avg_temp", "avg_hum", "status"
                ] if c in df_results.columns
            ]
            st.dataframe(df_results[preferred_columns], use_container_width=True, hide_index=True)
            
            # Render Map
            render_map(df_results, my_warehouses_df, delivery_points_df)

            st.markdown("#### Contacter les propriétaires")
            render_contact_owner_section(
                df_results=df_results,
                product_name=results_snapshot["product"],
                current_researcher_id=researcher_id,
            )
        else:
            st.info("Cette recherche n'avait retourné aucun entrepôt compatible.")
    else:
        st.info("Aucune recherche n'a encore été enregistrée dans votre historique.")

    # Fin de la section historique (div fermée dans le header)

    a, b = st.columns(2)
    with a:
        st.markdown('<div class="section-card"><h3 style="margin:0;">Entrepots importes</h3></div>', unsafe_allow_html=True)
        if my_warehouses_df.empty:
            st.info("Aucun entrepot importe pour le moment.")
        else:
            st.dataframe(my_warehouses_df, use_container_width=True, hide_index=True)
        # Section card closing handled in header


    with b:
        st.markdown('<div class="section-card"><h3 style="margin:0;">Points de livraison</h3></div>', unsafe_allow_html=True)
        if delivery_points_df.empty:
            st.info("Aucun point de livraison enregistre pour le moment.")
        else:
            st.dataframe(delivery_points_df, use_container_width=True, hide_index=True)
        # Section card closing handled in header



elif current_view == "responses":

    # ── CSS partagé messagerie chercheur ──────────────────────────────────
    st.markdown("""
    <style>
    .req-status-bar {
        display:flex; gap:8px; margin-bottom:18px; flex-wrap:wrap;
    }
    .status-pill {
        padding:6px 14px; border-radius:999px; font-size:13px; font-weight:600;
    }
    .pill-pending  { background:#fef3c7; color:#92400e; border:1px solid #fde68a; }
    .pill-accepted { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
    .pill-rejected { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; }
    .req-info-banner {
        background:linear-gradient(90deg,#f0f7ff,#fff);
        border:1px solid #bfdbfe; border-radius:12px;
        padding:12px 16px; margin-bottom:14px; font-size:13px; color:#1e40af;
    }
    .chat-wrap {
        background:#f8fbff; border:1px solid #e2e8f0;
        border-radius:16px; padding:18px; margin-bottom:8px;
        min-height:200px; max-height:420px; overflow-y:auto;
    }
    .bubble-r { display:flex; align-items:flex-end; gap:10px; margin-bottom:12px; }
    .bubble-r.right { flex-direction:row-reverse; }
    .av {
        width:32px; height:32px; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        font-weight:800; font-size:13px; flex-shrink:0;
    }
    .av-me  { background:#dbeafe; color:#1d4ed8; }
    .av-them{ background:#dcfce7; color:#166534; }
    .bbl {
        max-width:65%; padding:9px 14px; border-radius:16px;
        font-size:14px; line-height:1.5;
    }
    .bbl.right {
        background:linear-gradient(135deg,#2563eb,#1d4ed8);
        color:#fff; border-bottom-right-radius:3px;
    }
    .bbl.left {
        background:#fff; border:1px solid #e2e8f0;
        color:#1e293b; border-bottom-left-radius:3px;
        box-shadow:0 2px 6px rgba(0,0,0,0.04);
    }
    .bbl-ts { font-size:10px; opacity:0.55; margin-top:3px; }
    .timeline-dot {
        width:10px; height:10px; border-radius:50%; display:inline-block;
        margin-right:6px;
    }
    .dot-pending  { background:#f59e0b; }
    .dot-accepted { background:#22c55e; }
    .dot-rejected { background:#ef4444; }
    </style>
    """, unsafe_allow_html=True)

    # ── Données fraîches ────────────────────────────────────────────────────
    fresh_discussions = load_researcher_discussions(researcher_id)

    # ── KPIs rapides ────────────────────────────────────────────────────────
    st.markdown("## 💬 Messagerie & Suivi des demandes")
    kc1, kc2, kc3 = st.columns(3)
    n_pending  = len(fresh_discussions[fresh_discussions["status"] == REQUEST_PENDING])  if not fresh_discussions.empty else 0
    n_accepted = len(fresh_discussions[fresh_discussions["status"] == REQUEST_ACCEPTED]) if not fresh_discussions.empty else 0
    n_rejected = len(fresh_discussions[fresh_discussions["status"] == "rejected"])       if not fresh_discussions.empty else 0
    with kc1:
        st.markdown(f'<div style="background:#fef3c7;border-radius:12px;padding:14px;text-align:center;"><div style="font-size:22px;font-weight:800;color:#92400e;">{n_pending}</div><div style="font-size:12px;color:#78350f;">⏳ En attente</div></div>', unsafe_allow_html=True)
    with kc2:
        st.markdown(f'<div style="background:#dcfce7;border-radius:12px;padding:14px;text-align:center;"><div style="font-size:22px;font-weight:800;color:#166534;">{n_accepted}</div><div style="font-size:12px;color:#14532d;">✅ Acceptées</div></div>', unsafe_allow_html=True)
    with kc3:
        st.markdown(f'<div style="background:#fee2e2;border-radius:12px;padding:14px;text-align:center;"><div style="font-size:22px;font-weight:800;color:#991b1b;">{n_rejected}</div><div style="font-size:12px;color:#7f1d1d;">❌ Refusées</div></div>', unsafe_allow_html=True)

    st.write("")

    if fresh_discussions.empty:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px;color:#94a3b8;">
            <div style="font-size:44px;margin-bottom:12px;">📭</div>
            <p style="font-size:16px;">Aucune demande envoyée pour le moment.<br/>
            Faites une recherche et contactez un propriétaire pour démarrer.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # ── Onglets par statut ───────────────────────────────────────────────
        tab_all, tab_acc, tab_pend, tab_ref = st.tabs([
            f"📋 Toutes ({len(fresh_discussions)})",
            f"✅ Chat actif ({n_accepted})",
            f"⏳ En attente ({n_pending})",
            f"❌ Refusées ({n_rejected})",
        ])

        def render_status_badge(status):
            badges = {
                REQUEST_PENDING:  '<span class="status-pill pill-pending">⏳ En attente</span>',
                REQUEST_ACCEPTED: '<span class="status-pill pill-accepted">✅ Acceptée</span>',
                "rejected":       '<span class="status-pill pill-rejected">❌ Refusée</span>',
            }
            return badges.get(status, f'<span class="status-pill">{status}</span>')

        # ── Onglet : Toutes ──────────────────────────────────────────────────
        with tab_all:
            for _, disc in fresh_discussions.iterrows():
                wh   = disc.get("warehouse_name", disc.get("warehouse_id", "—"))
                addr = disc.get("warehouse_address", "")
                own  = disc.get("owner_first_name", "Propriétaire")
                prod = disc.get("product_name", "—")
                ts   = disc.get("created_at", "")
                badge = render_status_badge(disc["status"])
                st.markdown(f"""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;
            padding:16px;margin-bottom:12px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <div style="font-weight:700;font-size:15px;color:#0f172a;">🏢 {wh}</div>
      <div style="font-size:12px;color:#64748b;margin-top:2px;">📍 {addr}</div>
    </div>
    {badge}
  </div>
  <div style="font-size:13px;color:#475569;margin-top:8px;">
    👤 <b>{own}</b> &nbsp;|&nbsp; 📦 <b>{prod}</b> &nbsp;|&nbsp; 🕐 {ts}
  </div>
</div>""", unsafe_allow_html=True)

        # ── Onglet : Chat actif ──────────────────────────────────────────────
        with tab_acc:
            accepted_discs = fresh_discussions[fresh_discussions["status"] == REQUEST_ACCEPTED]
            if accepted_discs.empty:
                st.markdown("""<div style="text-align:center;padding:30px;color:#94a3b8;">
                    <div style="font-size:32px;">💬</div>
                    <p>Aucune conversation ouverte.<br>Un propriétaire doit d'abord accepter votre demande.</p>
                </div>""", unsafe_allow_html=True)
            else:
                options = {
                    f"🏢 {row['warehouse_name']}  ·  👤 {row['owner_first_name']}": row["request_id"]
                    for _, row in accepted_discs.iterrows()
                }
                sel_label = st.selectbox("Conversation", list(options.keys()), key="researcher_chat_sel")
                sel_id = options[sel_label]
                sel_row = accepted_discs[accepted_discs["request_id"] == sel_id].iloc[0]

                # Bandeau infos
                st.markdown(f"""<div class="req-info-banner">
                    🏢 <b>{sel_row.get('warehouse_name','')}</b> &nbsp;|&nbsp;
                    📦 <b>{sel_row.get('product_name','')}</b> &nbsp;|&nbsp;
                    👤 Propriétaire : <b>{sel_row.get('owner_first_name','')}</b>
                </div>""", unsafe_allow_html=True)

                # Messages
                msgs = get_chat_messages(sel_id)
                if msgs.empty:
                    st.markdown("""<div style="text-align:center;padding:24px;color:#94a3b8;">
                        <div style="font-size:28px;">👋</div>
                        <p>Le propriétaire a accepté. Envoyez votre premier message !</p>
                    </div>""", unsafe_allow_html=True)
                else:
                    bubbles = ""
                    for _, m in msgs.iterrows():
                        is_me = m["sender_id"] == researcher_id
                        side  = "right" if is_me else "left"
                        av_cls = "av-me" if is_me else "av-them"
                        label  = "Vous" if is_me else sel_row.get("owner_first_name", "P")
                        init   = "V" if is_me else (sel_row.get("owner_first_name", "P") or "P")[0].upper()
                        ts_val = str(m["created_at"])[-19:-3] if len(str(m["created_at"])) >= 19 else str(m["created_at"])
                        bubbles += f"""
<div class="bubble-r {side}">
  <div class="av {av_cls}">{init}</div>
  <div>
    <div style="font-size:11px;color:#94a3b8;margin-bottom:3px;{'text-align:right' if is_me else ''}">{label}</div>
    <div class="bbl {side}">
      {m['message']}
      <div class="bbl-ts">{ts_val}</div>
    </div>
  </div>
</div>"""
                    st.markdown(f'<div class="chat-wrap">{bubbles}</div>', unsafe_allow_html=True)

                # Saisie message
                col_txt, col_send = st.columns([5, 1])
                with col_txt:
                    new_msg = st.text_input(
                        "Message",
                        placeholder="Écrire un message...",
                        key=f"researcher_input_{sel_id}",
                        label_visibility="collapsed",
                    )
                with col_send:
                    if st.button("➤ Envoyer", key=f"researcher_send_{sel_id}", use_container_width=True, type="primary"):
                        if new_msg and new_msg.strip():
                            ok, fb = send_chat_message(sel_id, researcher_id, "researcher", new_msg)
                            if ok:
                                st.rerun()
                            else:
                                st.warning(fb)
                        else:
                            st.warning("Message vide.")

                col_ref_btn, _ = st.columns([1, 4])
                with col_ref_btn:
                    if st.button("🔄 Rafraîchir", key=f"refresh_r_{sel_id}"):
                        st.rerun()

                st.divider()
                import sqlite3
                from utils.db import DB_PATH, execute_query
                conn = sqlite3.connect(DB_PATH)
                df_offer = pd.read_sql_query("SELECT reservation_id, global_score, reason FROM reservations WHERE warehouse_id = ? AND researcher_id = ? AND status = 'pending'", conn, params=(sel_row['warehouse_id'], researcher_id))
                df_confirmed = pd.read_sql_query("SELECT reservation_id FROM reservations WHERE warehouse_id = ? AND researcher_id = ? AND status = 'confirmed'", conn, params=(sel_row['warehouse_id'], researcher_id))
                conn.close()
                
                if not df_offer.empty:
                    st.markdown("### 🤝 Offre en attente")
                    offer_row = df_offer.iloc[0]
                    st.info(f"**Offre de location reçue du propriétaire**\n- Prix : {offer_row['global_score']} DH\n- Date de début : {offer_row['reason']}")
                    
                    if st.button("Accepter l'offre et débloquer l'accès IoT", type="primary", key=f"accept_offer_{sel_id}"):
                        execute_query("UPDATE reservations SET status = 'confirmed' WHERE reservation_id = ?", (str(offer_row['reservation_id']),))
                        send_chat_message(sel_id, int(researcher_id), "researcher", f"✅ **OFFRE ACCEPTÉE** (Prix : {offer_row['global_score']} DH). L'accès au Dashboard IoT a été débloqué.")
                        st.success("Offre acceptée ! Vous pouvez maintenant accéder au Dashboard IoT pour cet entrepôt.")
                        st.rerun()
                elif not df_confirmed.empty:
                    st.markdown("### 📊 Suivi IoT Actif")
                    st.success("L'offre a été acceptée. Vous avez accès au suivi des capteurs (Température / Humidité) de cet entrepôt en temps réel.")
                    if st.button("Accéder au Dashboard IoT", type="primary", key=f"goto_iot_{sel_id}"):
                        st.switch_page("pages/8_Dashboard_IoT.py")

        # ── Onglet : En attente ──────────────────────────────────────────────
        with tab_pend:
            pending_discs = fresh_discussions[fresh_discussions["status"] == REQUEST_PENDING]
            if pending_discs.empty:
                st.info("Aucune demande en attente de réponse.")
            else:
                st.caption("Ces demandes attendent la réponse du propriétaire.")
                for _, disc in pending_discs.iterrows():
                    st.markdown(f"""
<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:12px;
            padding:14px;margin-bottom:10px;">
  <div style="font-weight:700;color:#92400e;">⏳ {disc.get('warehouse_name','—')}</div>
  <div style="font-size:13px;color:#78350f;margin-top:4px;">
    📦 {disc.get('product_name','—')} &nbsp;|&nbsp;
    👤 {disc.get('owner_first_name','—')} &nbsp;|&nbsp;
    🕐 {disc.get('created_at','')}
  </div>
</div>""", unsafe_allow_html=True)

        # ── Onglet : Refusées ────────────────────────────────────────────────
        with tab_ref:
            rejected_discs = fresh_discussions[fresh_discussions["status"] == "rejected"]
            if rejected_discs.empty:
                st.success("Aucune demande refusée !")
            else:
                for _, disc in rejected_discs.iterrows():
                    st.markdown(f"""
<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;
            padding:14px;margin-bottom:10px;">
  <div style="font-weight:700;color:#991b1b;">❌ {disc.get('warehouse_name','—')}</div>
  <div style="font-size:13px;color:#7f1d1d;margin-top:4px;">
    📦 {disc.get('product_name','—')} &nbsp;|&nbsp;
    👤 {disc.get('owner_first_name','—')} &nbsp;|&nbsp;
    🕐 {disc.get('created_at','')}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


st.write("")
if st.button("🚪 Se déconnecter", key="logout_researcher"):
    st.session_state.clear()
    st.switch_page("app.py")

# Rendu du chatbot OptiBot
from components.chatbot import render_optibot
render_optibot()
