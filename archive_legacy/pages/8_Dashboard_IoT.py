import streamlit as st
import time
from datetime import timedelta
from utils.db import load_sql_to_dataframe
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from utils.product_conditions import PRODUCT_CONDITIONS
from utils.ui import hide_sidebar

st.set_page_config(page_title="Suivi Temps Réel IoT", page_icon="⏱️", layout="wide")
hide_sidebar()

# Bouton de retour
col_back, col_title = st.columns([1, 8])
with col_back:
    st.write("") # Espace
    if st.button("🔙 Retour"):
        role_back = st.session_state.get('role', '')
        if role_back == "researcher":
            st.switch_page("pages/9_Interface_Chercheur.py")
        elif role_back == "owner":
            st.switch_page("pages/4_Interface_Proprietaire.py")
        else:
            st.switch_page("app.py")

with col_title:
    st.title("⏱️ Suivi Temps Réel IoT")

st.caption("Simulation d'un flux de données temps réel (1 relevé = 1 heure).")

# =====================================================
# Vérification de connexion & Rôles
# =====================================================
if 'logged_in' not in st.session_state or not st.session_state.get('logged_in'):
    st.warning("🔒 Accès refusé. Veuillez vous connecter d'abord.")
    st.switch_page("pages/1_Login.py")
    st.stop()

user_id = st.session_state.get('user_id')
role = st.session_state.get('role')
user_name = f"{st.session_state.get('user', {}).get('first_name', '')} {st.session_state.get('user', {}).get('last_name', '')}"

st.sidebar.markdown(f"**Utilisateur :** {user_name}")
st.sidebar.markdown(f"**Rôle :** {role.capitalize()}")

# =====================================================
# Récupération des entrepôts selon le rôle
# =====================================================
@st.cache_data
def get_user_warehouses(u_id, u_role):
    import pandas as pd
    from utils.db import get_db_connection
    conn = get_db_connection()
    
    if u_role == 'owner':
        # Entrepôts possédés par le propriétaire
        query = "SELECT warehouse_id, name FROM warehouses WHERE owner_id = ?"
        df = pd.read_sql_query(query, conn, params=(u_id,))
    elif u_role == 'researcher':
        # Entrepôts réservés OU importés par le chercheur
        query = """
            SELECT DISTINCT w.warehouse_id, w.name 
            FROM warehouses w
            JOIN reservations r ON w.warehouse_id = r.warehouse_id
            WHERE r.researcher_id = ? AND r.status = 'confirmed'
            UNION
            SELECT DISTINCT id_entrepot as warehouse_id, nom as name
            FROM my_warehouse
            WHERE researcher_id = ?
        """
        df = pd.read_sql_query(query, conn, params=(u_id, u_id))
    else:
        # Admin : voit tout
        query = "SELECT warehouse_id, name FROM warehouses"
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df

df_user_wh = get_user_warehouses(user_id, role)

if df_user_wh.empty:
    st.info("👋 Bienvenue ! Vous n'avez pas encore d'entrepôt à superviser.")
    if role == 'researcher':
        st.write("Importez vos données ou réservez un entrepôt dans l'interface chercheur.")
    elif role == 'owner':
        st.write("Ajoutez vos entrepôts au catalogue pour commencer le suivi.")
    st.stop()

# Sélecteur de contexte (Entrepôt d'abord pour pouvoir récupérer le bon produit)
col_ctx1, col_ctx2 = st.columns(2)

with col_ctx2:
    # Créer un dictionnaire pour l'affichage (Nom - ID)
    wh_options = {f"{row['name']} ({row['warehouse_id']})": row['warehouse_id'] for _, row in df_user_wh.iterrows()}
    selected_label = st.selectbox("Entrepôt à superviser", list(wh_options.keys()))
    entrepot = wh_options[selected_label]

with col_ctx1:
    if role == 'researcher':
        # Le chercheur ne voit que le produit spécifique associé à sa demande de contact pour cet entrepôt
        from utils.db import load_sql_to_dataframe
        hist = load_sql_to_dataframe("SELECT product_name FROM contact_requests WHERE researcher_id = ? AND warehouse_id = ? ORDER BY created_at DESC LIMIT 1", (user_id, entrepot))
        
        if not hist.empty and hist.iloc[0]["product_name"]:
            re_prod = hist.iloc[0]["product_name"]
        else:
            # Fallback
            re_prod = st.session_state.get("researcher_search_product", list(PRODUCT_CONDITIONS.keys())[0])
            
        st.markdown(f"**Produit suivi :** {re_prod}")
        st.caption("Verrouillé sur le produit de votre réservation.")
        produit = re_prod
    else:
        # Le propriétaire peut tout voir
        produit = st.selectbox("Produit suivi", list(PRODUCT_CONDITIONS.keys()))

cond = PRODUCT_CONDITIONS[produit]
t_min, t_max = cond["temperature"]["min"], cond["temperature"]["max"]
h_min, h_max = cond["humidite"]["min"], cond["humidite"]["max"]

st.markdown(f"**Conditions optimales pour {produit}** : T° [{t_min}°C - {t_max}°C] | H% [{h_min}% - {h_max}%]")
st.divider()

# Initialisation de la simulation dans la session
if "rt_index" not in st.session_state:
    st.session_state.rt_index = 0
if "rt_running" not in st.session_state:
    st.session_state.rt_running = False

# Chargement des données pour la simulation
query = f"SELECT recorded_at as datetime, temp_sensor_1, temp_sensor_2, temp_sensor_3, hum_sensor_1, hum_sensor_2, hum_sensor_3 FROM iot_readings WHERE warehouse_id = '{entrepot}' ORDER BY recorded_at"
df_rt = load_sql_to_dataframe(query)

if df_rt.empty:
    st.error("Pas de données pour cet entrepôt.")
    st.stop()

# Nettoyage et aggrégation
cols_t = ["temp_sensor_1", "temp_sensor_2", "temp_sensor_3"]
cols_h = ["hum_sensor_1", "hum_sensor_2", "hum_sensor_3"]

for col in cols_t + cols_h:
    df_rt[col] = df_rt[col].interpolate(method='linear', limit_direction='both')
    df_rt[col] = df_rt[col].rolling(window=3, min_periods=1).mean()

df_rt["T"] = df_rt[cols_t].mean(axis=1)
df_rt["H"] = df_rt[cols_h].mean(axis=1)

max_idx = len(df_rt) - 1

st.markdown("### 🕹️ Contrôle du temps")
col_btn1, col_btn2, col_btn3 = st.columns([1,1,4])
with col_btn1:
    if st.button("▶️ Lecture auto" if not st.session_state.rt_running else "⏸️ Pause", use_container_width=True):
        st.session_state.rt_running = not st.session_state.rt_running
        st.rerun()
with col_btn2:
    if st.button("⏩ +1 Heure", use_container_width=True):
        st.session_state.rt_index = min(st.session_state.rt_index + 1, max_idx)
        st.rerun()
with col_btn3:
    new_idx = st.slider("Naviguer dans le temps", min_value=0, max_value=max_idx, value=min(st.session_state.rt_index, max_idx), label_visibility="collapsed")
    if new_idx != st.session_state.rt_index:
        st.session_state.rt_index = new_idx
        st.session_state.rt_running = False
        st.rerun()

idx = min(st.session_state.rt_index, max_idx)
current_data = df_rt.iloc[idx]

# Affichage des KPIs
st.subheader(f"📡 Relevé du {current_data['datetime']}")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

current_t = current_data["T"]
current_h = current_data["H"]

delta_t = 0
statut_t = "Optimal"
color_t = "#27ae60"
if current_t < t_min:
    delta_t = current_t - t_min
    statut_t = "Critique Bas" if current_t < (t_min + cond["temperature"]["marge_bas"]) else "Alerte Basse"
    color_t = "#e74c3c" if "Critique" in statut_t else "#f39c12"
elif current_t > t_max:
    delta_t = current_t - t_max
    statut_t = "Critique Haut" if current_t > (t_max + cond["temperature"]["marge_haut"]) else "Alerte Haute"
    color_t = "#e74c3c" if "Critique" in statut_t else "#f39c12"
    
delta_h = 0
statut_h = "Optimal"
color_h = "#27ae60"
if current_h < h_min:
    delta_h = current_h - h_min
    statut_h = "Critique Bas" if current_h < (h_min + cond["humidite"]["marge_bas"]) else "Alerte Basse"
    color_h = "#e74c3c" if "Critique" in statut_h else "#f39c12"
elif current_h > h_max:
    delta_h = current_h - h_max
    statut_h = "Critique Haut" if current_h > (h_max + cond["humidite"]["marge_haut"]) else "Alerte Haute"
    color_h = "#e74c3c" if "Critique" in statut_h else "#f39c12"
    
# Calcul simple du "Score de stabilité" instantané
stability_score = 100
if statut_t != "Optimal": stability_score -= 25 if "Critique" in statut_t else 10
if statut_h != "Optimal": stability_score -= 25 if "Critique" in statut_h else 10

# Système d'alerte Email basé sur le dépassement du temps de tolérance
# On recule dans l'historique pour compter combien de relevés consécutifs sont hors normes (1 relevé = 1 heure)
consecutive_t_bad = 0
for i in range(idx, -1, -1):
    if df_rt.iloc[i]["T"] < t_min or df_rt.iloc[i]["T"] > t_max:
        consecutive_t_bad += 1
    else:
        break

consecutive_h_bad = 0
for i in range(idx, -1, -1):
    if df_rt.iloc[i]["H"] < h_min or df_rt.iloc[i]["H"] > h_max:
        consecutive_h_bad += 1
    else:
        break

duration_t_bad = consecutive_t_bad * 1.0
duration_h_bad = consecutive_h_bad * 1.0

tol_t = cond["temperature"].get("temps_resistance_bas_min_h", 999) if current_t < t_min else cond["temperature"].get("temps_resistance_haut_min_h", 999)
tol_h = cond["humidite"].get("temps_resistance_bas_min_h", 999) if current_h < h_min else cond["humidite"].get("temps_resistance_haut_min_h", 999)

trigger_t = (statut_t != "Optimal") and (duration_t_bad >= tol_t)
trigger_h = (statut_h != "Optimal") and (duration_h_bad >= tol_h)

# Styles CSS personnalisés pour les KPIs
st.markdown("""
<style>
.metric-box {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    border-left: 4px solid #3498db;
    height: 100%;
}
.metric-title { color: #7f8c8d; font-size: 0.9em; font-weight: bold; }
.metric-value { color: #2c3e50; font-size: 1.8em; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

with kpi1:
    st.markdown(f"<div class='metric-box' style='border-left-color:{color_t};'><div class='metric-title'>🌡️ Température</div><div class='metric-value'>{current_t:.1f} °C</div><div style='color:{color_t};font-size:0.8em;'>{statut_t} (Δ {delta_t:+.1f})</div></div>", unsafe_allow_html=True)
with kpi2:
    st.markdown(f"<div class='metric-box' style='border-left-color:{color_h};'><div class='metric-title'>💧 Humidité</div><div class='metric-value'>{current_h:.1f} %</div><div style='color:{color_h};font-size:0.8em;'>{statut_h} (Δ {delta_h:+.1f})</div></div>", unsafe_allow_html=True)
with kpi3:
    if statut_t == "Optimal" and statut_h == "Optimal":
        content_res = "<div style='color:#27ae60;'>Optimal (Aucun danger)</div>"
    else:
        content_res = ""
        if statut_t != "Optimal":
            color = "#e74c3c" if duration_t_bad >= tol_t else "#f39c12"
            content_res += f"<div style='color:{color}; font-size: 0.9em; margin-bottom: 5px;'>T°: {duration_t_bad}h / {tol_t}h tolérées</div>"
        if statut_h != "Optimal":
            color = "#e74c3c" if duration_h_bad >= tol_h else "#f39c12"
            content_res += f"<div style='color:{color}; font-size: 0.9em;'>Hum: {duration_h_bad}h / {tol_h}h tolérées</div>"

    st.markdown(f"<div class='metric-box'><div class='metric-title'>⏳ Consommation Tolérance</div><div style='margin-top:10px; font-weight:bold;'>{content_res}</div></div>", unsafe_allow_html=True)
with kpi4:
    st.markdown(f"<div class='metric-box'><div class='metric-title'>🎯 Indice Stabilité</div><div class='metric-value'>{stability_score}/100</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if "last_alert_sent" not in st.session_state:
    st.session_state.last_alert_sent = False

if trigger_t or trigger_h:
    reasons = []
    if trigger_t: reasons.append(f"T° hors normes depuis {duration_t_bad}h (Tolérance: {tol_t}h)")
    if trigger_h: reasons.append(f"Humidité hors normes depuis {duration_h_bad}h (Tolérance: {tol_h}h)")
    
    # Affichage continu de l'alerte sur le Dashboard tant que la crise dure
    st.error("🚨 **DANGER - DÉGRADATION DU PRODUIT** : " + " | ".join(reasons))
    
    # Envoi de l'email une seule fois par événement
    if not st.session_state.last_alert_sent:
        st.toast("📧 ALERTE EMAIL ENVOYÉE au chercheur et propriétaire", icon="🚨")
        st.session_state.last_alert_sent = True
elif not trigger_t and not trigger_h and st.session_state.last_alert_sent:
    # Réarmer le flag d'email si la situation est résolue
    st.session_state.last_alert_sent = False

st.markdown("<br>", unsafe_allow_html=True)

# Toggle pour la vue graphique
view_mode = st.radio("Affichage du graphique :", ["Fenêtre glissante (24 dernières heures)", "Historique complet"], horizontal=True)

if "Fenêtre" in view_mode:
    window = 24 # 24 derniers points (24 heures)
    start_idx = max(0, idx - window)
    title_graph = "Dynamique Temps Réel (Fenêtre glissante)"
else:
    start_idx = 0
    title_graph = "Historique Complet"

df_window = df_rt.iloc[start_idx:idx+1].copy()

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(go.Scatter(x=df_window["datetime"], y=df_window["T"], name="Température (°C)", line=dict(color="#e74c3c", width=3)), secondary_y=False)
fig.add_trace(go.Scatter(x=df_window["datetime"], y=df_window["H"], name="Humidité (%)", line=dict(color="#3498db", dash="dash")), secondary_y=True)

# Zones optimales
fig.add_hrect(y0=t_min, y1=t_max, fillcolor="green", opacity=0.1, line_width=0, secondary_y=False)

fig.update_layout(title=title_graph, height=400, margin=dict(l=0, r=0, t=40, b=0), plot_bgcolor="white")
st.plotly_chart(fig, use_container_width=True)

# Auto-refresh mechanism
if st.session_state.rt_running:
    time.sleep(2) # Attendre 2 secondes (simulation de l'écoulement du temps)
    st.session_state.rt_index += 1
    st.rerun()
