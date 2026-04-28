import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Optimization Lab – OptiStock", page_icon="🚀", layout="wide")

# ── Auth ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    st.warning("🔒 Accès refusé. Veuillez vous connecter.")
    st.switch_page("pages/1_Login.py")
    st.stop()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.lab-hero {
    background: linear-gradient(135deg, #0a1628 0%, #005da7 60%, #fe893a 100%);
    border-radius: 16px; padding: 32px 40px; color: white; margin-bottom: 24px;
}
.lab-hero h1 { font-size: 2rem; font-weight: 700; margin: 0 0 8px 0; }
.lab-hero p  { opacity: .85; margin: 0; font-size: 1rem; }
.solver-badge {
    display: inline-block; background: #1e3a5f; color: #7ec8e3;
    border: 1px solid #2d5a8e; border-radius: 20px;
    padding: 4px 14px; font-size: 12px; font-weight: 600; margin: 4px 2px;
}
.result-card {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 20px; margin-bottom: 16px;
}
.kpi { text-align:center; padding:16px; background:#f8fafc;
       border-radius:10px; border:1px solid #e2e8f0; }
.kpi-val { font-size:1.8rem; font-weight:800; color:#005da7; }
.kpi-lab { font-size:.8rem; color:#64748b; margin-top:4px; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lab-hero">
  <h1>🚀 Optimization Lab</h1>
  <p>Planifiez l'expansion de votre réseau logistique (Focus Région Béni Mellal - Khénifra).</p>
</div>
""", unsafe_allow_html=True)

# ── Imports moteurs ───────────────────────────────────────────────────────────
from core.routing import OptiRouteOptimizer, _haversine
from core.optimizer_mip import MipExpansionOptimizer, get_available_solver as mip_solver
from core.optimizer_ortools import ORToolsLogisticOptimizer, get_available_solver as ortools_solver

# ── Données par défaut (Scénario Béni Mellal - Khénifra) ──────────────────────
DEFAULT_EXISTING = [
    {"name": "Khouribga",  "lat": 32.8810, "lon": -6.9063, "capacity": 500},
    {"name": "Fquih Ben Salah", "lat": 32.5009, "lon": -6.6906, "capacity": 400},
]
DEFAULT_CANDIDATES = [
    {"name": "Béni Mellal", "lat": 32.3373, "lon": -6.3498, "capacity": 300},
    {"name": "Khénifra",    "lat": 32.9357, "lon": -5.6696, "capacity": 350},
    {"name": "Azilal",      "lat": 31.9641, "lon": -6.5590, "capacity": 250},
]
DEFAULT_CLIENTS = [
    {"name": "Kasba Tadla",  "lat": 32.5977, "lon": -6.2684, "demand": 120},
    {"name": "Oued Zem",     "lat": 32.8627, "lon": -6.5615, "demand": 90},
    {"name": "Mrirt",        "lat": 33.1678, "lon": -5.5681, "demand": 60},
    {"name": "Demnate",      "lat": 31.7311, "lon": -7.0361, "demand": 80},
    {"name": "Zaouiat Cheikh","lat":32.6514, "lon": -5.9206, "demand": 70},
]

# ── Session state init ────────────────────────────────────────────────────────
if "lab_existing"   not in st.session_state: st.session_state.lab_existing   = DEFAULT_EXISTING.copy()
if "lab_candidates" not in st.session_state: st.session_state.lab_candidates = DEFAULT_CANDIDATES.copy()
if "lab_clients"    not in st.session_state: st.session_state.lab_clients     = DEFAULT_CLIENTS.copy()
if "lab_results"    not in st.session_state: st.session_state.lab_results     = None

# ── Onglets ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Scénario", "🏗️ Choix du Site", "📦 Ordre de Livraison", "📊 Comparaison"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — Scénario
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📍 Configurer le scénario logistique")
    st.info("Saisissez les entrepôts existants, les sites candidats et les clients à livrer.")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 🏢 Entrepôts existants")
        existing_data = []
        for i, w in enumerate(st.session_state.lab_existing):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            name = c1.text_input("Nom", value=w["name"], key=f"ex_name_{i}", label_visibility="collapsed")
            lat  = c2.number_input("Lat", value=float(w["lat"]), key=f"ex_lat_{i}", format="%.4f", label_visibility="collapsed")
            lon  = c3.number_input("Lon", value=float(w["lon"]), key=f"ex_lon_{i}", format="%.4f", label_visibility="collapsed")
            cap  = c4.number_input("Cap", value=int(w["capacity"]), key=f"ex_cap_{i}", label_visibility="collapsed")
            existing_data.append({"name": name, "lat": lat, "lon": lon, "capacity": cap})

        st.markdown("#### 🎯 Sites Candidats")
        cand_data = []
        for i, c in enumerate(st.session_state.lab_candidates):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            name = c1.text_input("Nom", value=c["name"], key=f"ca_name_{i}", label_visibility="collapsed")
            lat  = c2.number_input("Lat", value=float(c["lat"]), key=f"ca_lat_{i}", format="%.4f", label_visibility="collapsed")
            lon  = c3.number_input("Lon", value=float(c["lon"]), key=f"ca_lon_{i}", format="%.4f", label_visibility="collapsed")
            cap  = c4.number_input("Cap", value=int(c["capacity"]), key=f"ca_cap_{i}", label_visibility="collapsed")
            cand_data.append({"name": name, "lat": lat, "lon": lon, "capacity": cap})

    with col_right:
        st.markdown("#### 👥 Clients à livrer")
        client_data = []
        for i, cl in enumerate(st.session_state.lab_clients):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            name = c1.text_input("Nom", value=cl["name"], key=f"cl_name_{i}", label_visibility="collapsed")
            lat  = c2.number_input("Lat", value=float(cl["lat"]), key=f"cl_lat_{i}", format="%.4f", label_visibility="collapsed")
            lon  = c3.number_input("Lon", value=float(cl["lon"]), key=f"cl_lon_{i}", format="%.4f", label_visibility="collapsed")
            dem  = c4.number_input("Dem", value=int(cl["demand"]), key=f"cl_dem_{i}", label_visibility="collapsed")
            client_data.append({"name": name, "lat": lat, "lon": lon, "demand": dem})

        n_to_add = st.number_input("Nombre de nouveaux entrepôts à ouvrir", min_value=1,
                                    max_value=len(cand_data), value=1)

        st.write("")
        shapefile_path = st.text_input("Chemin shapefile routier (optionnel)",
                                        value="data/gis/raods_BMK.shp",
                                        placeholder="data/gis/raods_BMK.shp")

        run = st.button("🚀 LANCER L'ANALYSE OPTIMISÉE", type="primary", use_container_width=True)

    # Carte de prévisualisation
    st.markdown("#### 🗺️ Carte du scénario")
    center_lat = np.mean([w["lat"] for w in existing_data + cand_data + client_data])
    center_lon = np.mean([w["lon"] for w in existing_data + cand_data + client_data])
    preview_map = folium.Map(location=[center_lat, center_lon], zoom_start=6,
                             tiles="CartoDB positron")
    for w in existing_data:
        folium.Marker([w["lat"], w["lon"]], popup=w["name"],
                      icon=folium.Icon(color="blue", icon="home")).add_to(preview_map)
    for c in cand_data:
        folium.Marker([c["lat"], c["lon"]], popup=c["name"],
                      icon=folium.Icon(color="orange", icon="star")).add_to(preview_map)
    for cl in client_data:
        folium.CircleMarker([cl["lat"], cl["lon"]], radius=6, color="#e74c3c",
                             fill=True, popup=cl["name"]).add_to(preview_map)
    st_folium(preview_map, height=380, use_container_width=True)

    st.caption("🔵 Entrepôts existants | 🟠 Candidats | 🔴 Clients")

    # ── Lancer l'analyse ─────────────────────────────────────────────────────
    if run:
        st.session_state.lab_existing   = existing_data
        st.session_state.lab_candidates = cand_data
        st.session_state.lab_clients    = client_data

        with st.spinner("⚙️ Calcul des matrices de distances (Dijkstra / Haversine)…"):
            optimizer_route = OptiRouteOptimizer(shapefile_path if shapefile_path else None)
            all_sites  = existing_data + cand_data
            sources    = [(s["lat"], s["lon"]) for s in all_sites]
            targets    = [(c["lat"], c["lon"]) for c in client_data]
            cost_matrix = optimizer_route.get_matrix(sources, targets, weight="time")
            routing_mode = optimizer_route.mode

        with st.spinner("🏗️ Sélection du meilleur site candidat…"):
            mip_opt = MipExpansionOptimizer()
            site_result = mip_opt.optimize_expansion(
                existing_data, cand_data, client_data, cost_matrix, n_to_add=int(n_to_add))

        with st.spinner("📦 Calcul de l'ordre de livraison (VRP)…"):
            # Construire matrice client×client depuis le meilleur site
            sel_idx  = site_result["selected_candidate_indices"]
            depot    = cand_data[sel_idx[0]] if sel_idx else existing_data[0]
            all_nodes = [depot] + client_data
            node_coords = [(n["lat"], n["lon"]) for n in all_nodes]
            n_nodes = len(node_coords)
            vrp_matrix = np.zeros((n_nodes, n_nodes))
            for i, (la1, lo1) in enumerate(node_coords):
                for j, (la2, lo2) in enumerate(node_coords):
                    vrp_matrix[i, j] = _haversine(la1, lo1, la2, lo2)

            ortools_opt = ORToolsLogisticOptimizer()
            vrp_result  = ortools_opt.compute_delivery_order(
                (depot["lat"], depot["lon"]),
                [(c["lat"], c["lon"]) for c in client_data],
                vrp_matrix,
                node_names=[c["name"] for c in client_data]
            )

        st.session_state.lab_results = {
            "routing_mode": routing_mode,
            "cost_matrix":  cost_matrix,
            "site_result":  site_result,
            "vrp_result":   vrp_result,
            "depot":        depot,
            "n_to_add":     n_to_add,
        }
        st.success("✅ Analyse terminée ! Consultez les onglets suivants.")
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — Choix du Site
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    res = st.session_state.lab_results
    if not res:
        st.info("▶️ Lancez d'abord l'analyse dans l'onglet **⚙️ Scénario**.")
    else:
        sr = res["site_result"]
        candidates = st.session_state.lab_candidates
        existing   = st.session_state.lab_existing
        clients    = st.session_state.lab_clients
        cost_matrix = res["cost_matrix"]

        st.markdown("### 🏗️ Résultat – Sélection du Meilleur Site")

        # Badges solveurs
        st.markdown(
            f'<span class="solver-badge">📍 Distances : {res["routing_mode"].upper()}</span>'
            f'<span class="solver-badge">🧮 Optimiseur : {sr.get("solver","?")}</span>',
            unsafe_allow_html=True)
        st.write("")

        # KPIs
        sel = sr.get("selected_candidate_indices", [])
        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(f'<div class="kpi"><div class="kpi-val">{", ".join(sr.get("selected_candidate_names", ["?"]))}</div><div class="kpi-lab">Site(s) sélectionné(s)</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi"><div class="kpi-val">{sr.get("objective_value", 0):.0f} min</div><div class="kpi-lab">Coût total pondéré</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi"><div class="kpi-val">{sr.get("savings_vs_random", 0):.1f}%</div><div class="kpi-lab">Économie vs aléatoire</div></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="kpi"><div class="kpi-val">{sr.get("status","?")}</div><div class="kpi-lab">Statut optimisation</div></div>', unsafe_allow_html=True)

        st.write("")

        # Carte résultat
        all_pts = existing + candidates + clients
        clat = np.mean([p["lat"] for p in all_pts])
        clon = np.mean([p["lon"] for p in all_pts])
        m = folium.Map(location=[clat, clon], zoom_start=6, tiles="CartoDB positron")

        for w in existing:
            folium.Marker([w["lat"], w["lon"]], popup=f"✅ Existant: {w['name']}",
                          icon=folium.Icon(color="blue", icon="home")).add_to(m)

        for i, c in enumerate(candidates):
            if i in sel:
                folium.Marker([c["lat"], c["lon"]], popup=f"🏆 SÉLECTIONNÉ: {c['name']}",
                              icon=folium.Icon(color="green", icon="star")).add_to(m)
            else:
                folium.Marker([c["lat"], c["lon"]], popup=f"❌ Non retenu: {c['name']}",
                              icon=folium.Icon(color="gray", icon="remove")).add_to(m)

        depot = res["depot"]
        n_existing = len(existing)
        assignments = sr.get("assignments", {})
        for i, cl in enumerate(clients):
            folium.CircleMarker([cl["lat"], cl["lon"]], radius=7, color="#e74c3c",
                                fill=True, popup=cl["name"]).add_to(m)
            # Ligne vers l'entrepôt assigné
            assigned_site = None
            for site_idx, client_list in assignments.items():
                if i in client_list:
                    all_sites = existing + candidates
                    if int(site_idx) < len(all_sites):
                        assigned_site = all_sites[int(site_idx)]
                    break
            if assigned_site:
                folium.PolyLine(
                    [[cl["lat"], cl["lon"]], [assigned_site["lat"], assigned_site["lon"]]],
                    color="#3b82f6", weight=1.5, opacity=0.6).add_to(m)

        st_folium(m, height=420, use_container_width=True)

        # Tableau des coûts par candidat
        st.markdown("### 📊 Analyse comparative des candidats")
        rows = []
        for i, c in enumerate(candidates):
            idx = n_existing + i
            if idx < len(cost_matrix):
                avg_cost = cost_matrix[idx].mean()
                max_cost = cost_matrix[idx].max()
                total_dem = sum(cl["demand"] * cost_matrix[idx, j]
                                for j, cl in enumerate(clients))
                rows.append({
                    "Candidat": c["name"],
                    "Coût Moy. (min)": round(avg_cost, 1),
                    "Coût Max (min)": round(max_cost, 1),
                    "Coût Pondéré Total": round(total_dem, 0),
                    "Sélectionné": "🏆 OUI" if i in sel else "❌ Non",
                })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — Ordre de Livraison
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    res = st.session_state.lab_results
    if not res:
        st.info("▶️ Lancez d'abord l'analyse dans l'onglet **⚙️ Scénario**.")
    else:
        vr = res["vrp_result"]
        depot = res["depot"]
        clients = st.session_state.lab_clients

        st.markdown("### 📦 Ordre Optimal de Livraison (VRP)")
        st.markdown(
            f'<span class="solver-badge">🚚 Solveur VRP : {vr.get("solver","?")}</span>',
            unsafe_allow_html=True)
        st.write("")

        order  = vr.get("delivery_order", [])
        labels = vr.get("route_labels", [])
        total  = vr.get("total_distance", 0)

        k1, k2, k3 = st.columns(3)
        k1.markdown(f'<div class="kpi"><div class="kpi-val">{depot["name"]}</div><div class="kpi-lab">Dépôt de départ</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="kpi"><div class="kpi-val">{len(order)}</div><div class="kpi-lab">Clients à livrer</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="kpi"><div class="kpi-val">{total:.1f} km</div><div class="kpi-lab">Distance totale tournée</div></div>', unsafe_allow_html=True)
        st.write("")

        # Séquence visuelle
        st.markdown("#### 🗺️ Séquence de livraison")
        route_map = folium.Map(location=[depot["lat"], depot["lon"]], zoom_start=6,
                               tiles="CartoDB positron")
        folium.Marker([depot["lat"], depot["lon"]],
                      popup=f"🏭 Dépôt: {depot['name']}",
                      icon=folium.Icon(color="green", icon="home")).add_to(route_map)

        route_coords = [(depot["lat"], depot["lon"])]
        for step, (ci, label) in enumerate(zip(order, labels)):
            if 0 <= ci < len(clients):
                cl = clients[ci]
                folium.Marker([cl["lat"], cl["lon"]],
                              popup=f"Étape {step+1}: {label}",
                              icon=folium.DivIcon(
                                  html=f'<div style="background:#e74c3c;color:white;border-radius:50%;'
                                       f'width:24px;height:24px;display:flex;align-items:center;'
                                       f'justify-content:center;font-weight:bold;font-size:11px;">{step+1}</div>'
                              )).add_to(route_map)
                route_coords.append((cl["lat"], cl["lon"]))

        route_coords.append((depot["lat"], depot["lon"]))
        if len(route_coords) > 2:
            folium.PolyLine(route_coords, color="#3b82f6", weight=3,
                            opacity=0.85, dash_array="8").add_to(route_map)
        st_folium(route_map, height=400, use_container_width=True)

        # Tableau séquence
        st.markdown("#### 📋 Feuille de route")
        steps = [{"Étape": 0, "Lieu": f"🏭 {depot['name']}", "Type": "Dépôt (départ)", "Demande": "—"}]
        for step, (ci, label) in enumerate(zip(order, labels)):
            dem = clients[ci]["demand"] if 0 <= ci < len(clients) else "?"
            steps.append({
                "Étape": step + 1,
                "Lieu": f"📦 {label}",
                "Type": "Livraison",
                "Demande": dem,
            })
        steps.append({"Étape": len(order)+1, "Lieu": f"🏭 {depot['name']}", "Type": "Retour dépôt", "Demande": "—"})
        st.dataframe(pd.DataFrame(steps), use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — Comparaison
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    res = st.session_state.lab_results
    if not res:
        st.info("▶️ Lancez d'abord l'analyse dans l'onglet **⚙️ Scénario**.")
    else:
        import plotly.graph_objects as go

        st.markdown("### 📊 Dashboard Comparatif des 3 Moteurs")

        sr = res["site_result"]
        vr = res["vrp_result"]
        candidates = st.session_state.lab_candidates
        clients    = st.session_state.lab_clients
        cost_matrix = res["cost_matrix"]
        n_existing  = len(st.session_state.lab_existing)

        # Résumé moteurs
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="result-card">
              <h4>🛣️ A. Moteur de Distance</h4>
              <p><b>Mode :</b> {res['routing_mode'].upper()}</p>
              <p><b>Rôle :</b> Calcule les temps de trajet réels entre entrepôts et clients.</p>
              <p><b>Avantage :</b> Dijkstra sur réseau routier > distances à vol d'oiseau.</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="result-card">
              <h4>🧮 B. Sélection du Site</h4>
              <p><b>Solveur :</b> {sr.get('solver','?')}</p>
              <p><b>Site retenu :</b> {', '.join(sr.get('selected_candidate_names',['?']))}</p>
              <p><b>Économie :</b> {sr.get('savings_vs_random',0):.1f}% vs choix aléatoire</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="result-card">
              <h4>🚚 C. Ordre de Livraison</h4>
              <p><b>Solveur :</b> {vr.get('solver','?')}</p>
              <p><b>Clients :</b> {len(vr.get('delivery_order',[]))}</p>
              <p><b>Distance totale :</b> {vr.get('total_distance',0):.1f} km</p>
            </div>""", unsafe_allow_html=True)

        st.write("")

        # Graphique : Coût par candidat
        cand_names, cand_costs = [], []
        sel = sr.get("selected_candidate_indices", [])
        demands = np.array([c["demand"] for c in clients])
        for i, c in enumerate(candidates):
            idx = n_existing + i
            if idx < len(cost_matrix):
                cost = float((cost_matrix[idx] * demands).sum())
                cand_names.append(c["name"])
                cand_costs.append(round(cost, 1))

        colors = ["#27ae60" if i in sel else "#bdc3c7" for i in range(len(cand_names))]
        fig = go.Figure(go.Bar(
            x=cand_names, y=cand_costs,
            marker_color=colors,
            text=[f"{v:,.0f}" for v in cand_costs],
            textposition="outside",
        ))
        fig.update_layout(
            title="Coût logistique pondéré par candidat (vert = sélectionné)",
            yaxis_title="Coût total (min × demande)",
            height=380,
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap matrice de coûts
        st.markdown("#### 🔥 Matrice de Distances (Entrepôts → Clients)")
        all_sites = st.session_state.lab_existing + candidates
        site_labels  = [s["name"] for s in all_sites]
        client_labels = [c["name"] for c in clients]
        fig2 = go.Figure(go.Heatmap(
            z=cost_matrix,
            x=client_labels,
            y=site_labels,
            colorscale="Blues",
            text=np.round(cost_matrix, 1),
            texttemplate="%{text}",
            colorbar=dict(title="min"),
        ))
        fig2.update_layout(
            title="Temps de trajet (minutes) — bleu foncé = plus proche",
            height=350,
            xaxis_title="Clients",
            yaxis_title="Entrepôts",
        )
        st.plotly_chart(fig2, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
if st.button("🚪 Déconnexion"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("pages/1_Login.py")
