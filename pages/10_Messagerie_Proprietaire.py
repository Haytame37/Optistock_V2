import streamlit as st
import pandas as pd

from core.messaging import (
    REQUEST_ACCEPTED,
    REQUEST_PENDING,
    ensure_messaging_schema,
    get_chat_messages,
    get_owner_requests,
    send_chat_message,
    update_contact_request_status,
)
from utils.ui import hide_sidebar

# =====================================================
# Config & Sécurité
# =====================================================
st.set_page_config(
    page_title="Messagerie | OptiStock",
    page_icon="💬",
    layout="wide",
)
hide_sidebar()

if not st.session_state.get("logged_in"):
    st.warning("🔒 Accès refusé. Veuillez vous connecter.")
    st.switch_page("pages/1_Login.py")
    st.stop()

if st.session_state.get("role") != "owner" and st.session_state.get("user", {}).get("role") != "owner":
    st.error("🔒 Accès réservé aux propriétaires.")
    st.stop()

ensure_messaging_schema()
owner_id  = st.session_state.get("user_id") or st.session_state.get("user", {}).get("user_id")
user_name = st.session_state.get("user", {}).get("first_name") or "Propriétaire"

# =====================================================
# CSS Premium
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

/* Hero */
.msg-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 60%, #2563eb 100%);
    border-radius: 20px;
    padding: 24px 32px;
    color: white;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.msg-hero h1 { margin:0; font-size:26px; font-weight:800; }
.msg-hero p  { margin:4px 0 0; color:rgba(255,255,255,0.7); font-size:14px; }
.hero-kpis   { display:flex; gap:20px; }
.hero-kpi    {
    background:rgba(255,255,255,0.12);
    border-radius:12px;
    padding:12px 20px;
    text-align:center;
    min-width:90px;
}
.hero-kpi-val  { font-size:24px; font-weight:800; }
.hero-kpi-lbl  { font-size:11px; opacity:0.75; margin-top:2px; }

/* Cartes de demande */
.req-card {
    background:#fff;
    border:1px solid #e2e8f0;
    border-radius:16px;
    padding:20px;
    margin-bottom:14px;
    box-shadow:0 4px 14px rgba(0,0,0,0.05);
    transition:box-shadow .2s, transform .15s;
}
.req-card:hover { box-shadow:0 8px 24px rgba(37,99,235,0.12); transform:translateY(-1px); }
.req-card-title { font-size:16px; font-weight:700; color:#0f172a; margin-bottom:6px; }
.req-card-row   { font-size:13px; color:#475569; margin:3px 0; }
.req-msg-box {
    background:#eff6ff;
    border-left:4px solid #2563eb;
    padding:10px 14px;
    border-radius:0 10px 10px 0;
    margin:12px 0 8px;
    font-size:13px;
    color:#1e40af;
    font-style:italic;
}

/* Badges */
.pill { padding:4px 12px; border-radius:999px; font-size:12px; font-weight:600; }
.pill-pending  { background:#fef3c7; color:#92400e; border:1px solid #fde68a; }
.pill-accepted { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
.pill-rejected { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; }

/* Chat */
.chat-info-bar {
    background:linear-gradient(90deg,#eff6ff,#fff);
    border:1px solid #bfdbfe;
    border-radius:12px;
    padding:12px 18px;
    margin-bottom:16px;
    font-size:13px;
    color:#1e40af;
}
.chat-box {
    background:#f8faff;
    border:1px solid #e2e8f0;
    border-radius:18px;
    padding:20px;
    min-height:300px;
    max-height:450px;
    overflow-y:auto;
    margin-bottom:14px;
}
.bwrap          { display:flex; align-items:flex-end; gap:10px; margin-bottom:14px; }
.bwrap.right    { flex-direction:row-reverse; }
.av {
    width:36px; height:36px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-weight:800; font-size:14px; flex-shrink:0;
}
.av-me   { background:#dbeafe; color:#1d4ed8; }
.av-them { background:#dcfce7; color:#166534; }
.bubble {
    max-width:65%;
    padding:10px 15px;
    border-radius:18px;
    font-size:14px;
    line-height:1.55;
}
.bubble.right {
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    color:#fff;
    border-bottom-right-radius:4px;
}
.bubble.left {
    background:#fff;
    border:1px solid #e2e8f0;
    color:#1e293b;
    border-bottom-left-radius:4px;
    box-shadow:0 2px 6px rgba(0,0,0,0.05);
}
.bts { font-size:10px; opacity:0.55; margin-top:4px; }

/* Empty state */
.empty-state {
    text-align:center; padding:50px 20px; color:#94a3b8;
}
.empty-state .ei { font-size:48px; margin-bottom:12px; }
.empty-state p   { font-size:15px; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# Données
# =====================================================
all_requests = get_owner_requests(owner_id)
pending_df   = all_requests[all_requests["status"] == REQUEST_PENDING]  if not all_requests.empty else pd.DataFrame()
accepted_df  = all_requests[all_requests["status"] == REQUEST_ACCEPTED] if not all_requests.empty else pd.DataFrame()
rejected_df  = all_requests[all_requests["status"] == "rejected"]       if not all_requests.empty else pd.DataFrame()
n_p, n_a, n_r = len(pending_df), len(accepted_df), len(rejected_df)

# =====================================================
# Hero
# =====================================================
st.markdown(f"""
<div class="msg-hero">
  <div>
    <h1>💬 Messagerie propriétaire</h1>
    <p>Bonjour {user_name} — gérez vos demandes et échangez avec les chercheurs</p>
  </div>
  <div class="hero-kpis">
    <div class="hero-kpi">
      <div class="hero-kpi-val" style="color:#fbbf24;">{n_p}</div>
      <div class="hero-kpi-lbl">En attente</div>
    </div>
    <div class="hero-kpi">
      <div class="hero-kpi-val" style="color:#4ade80;">{n_a}</div>
      <div class="hero-kpi-lbl">Chat actif</div>
    </div>
    <div class="hero-kpi">
      <div class="hero-kpi-val" style="color:#f87171;">{n_r}</div>
      <div class="hero-kpi-lbl">Refusées</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Bouton retour
if st.button("← Retour au tableau de bord", key="back_to_dashboard"):
    st.switch_page("pages/8_Interface_Proprietaire.py")

st.write("")

# =====================================================
# Onglets
# =====================================================
tab_pending, tab_chat, tab_history = st.tabs([
    f"📩 Nouvelles demandes {'🔴' if n_p > 0 else ''}  ({n_p})",
    f"💬 Chat actif  ({n_a})",
    f"📋 Historique  ({n_p + n_a + n_r})",
])

# ─── Onglet 1 : Nouvelles demandes ─────────────────────────────────────────
with tab_pending:
    if pending_df.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="ei">📭</div>
            <p>Aucune nouvelle demande pour le moment.<br/>
            Les chercheurs qui souhaitent vous contacter apparaîtront ici.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"**{n_p} demande(s) en attente de votre réponse**")
        st.write("")
        for _, req in pending_df.iterrows():
            wh_name  = req.get("warehouse_name", req.get("warehouse_id", "—"))
            wh_addr  = req.get("warehouse_address", "")
            r_name   = req.get("researcher_first_name", "Chercheur")
            product  = req.get("product_name", "—")
            message  = req.get("message", "")
            req_id   = req["request_id"]
            created  = req.get("created_at", "")

            st.markdown(f"""
<div class="req-card">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div class="req-card-title">🏢 {wh_name}</div>
    <span class="pill pill-pending">⏳ En attente</span>
  </div>
  <div class="req-card-row">📍 {wh_addr}</div>
  <div class="req-card-row">👤 <b>Chercheur :</b> {r_name} &nbsp;|&nbsp; 📦 <b>Produit :</b> {product}</div>
  <div class="req-card-row">🕐 Reçu le {created}</div>
  <div class="req-msg-box">"{message}"</div>
</div>""", unsafe_allow_html=True)

            col_acc, col_ref, col_space = st.columns([2, 2, 5])
            with col_acc:
                if st.button("✅ Accepter", key=f"acc_{req_id}", use_container_width=True, type="primary"):
                    if update_contact_request_status(req_id, owner_id, REQUEST_ACCEPTED):
                        st.success("✅ Demande acceptée ! Rendez-vous dans l'onglet Chat actif.")
                        st.rerun()
            with col_ref:
                if st.button("❌ Refuser", key=f"ref_{req_id}", use_container_width=True):
                    if update_contact_request_status(req_id, owner_id, "rejected"):
                        st.warning("Demande refusée.")
                        st.rerun()
            st.divider()

# ─── Onglet 2 : Chat actif ─────────────────────────────────────────────────
with tab_chat:
    if accepted_df.empty:
        st.markdown("""
        <div class="empty-state">
            <div class="ei">💬</div>
            <p>Aucune conversation active.<br/>
            Acceptez une demande pour démarrer le chat avec un chercheur.</p>
        </div>""", unsafe_allow_html=True)
    else:
        # Sélecteur de conversation
        conv_options = {
            f"🏢 {row['warehouse_name']}  ·  👤 {row['researcher_first_name']}": row["request_id"]
            for _, row in accepted_df.iterrows()
        }
        sel_label  = st.selectbox("Conversation", list(conv_options.keys()), key="owner_conv_sel")
        sel_req_id = conv_options[sel_label]
        sel_row    = accepted_df[accepted_df["request_id"] == sel_req_id].iloc[0]

        # Bandeau infos
        st.markdown(f"""
<div class="chat-info-bar">
  🏢 <b>{sel_row.get('warehouse_name','')}</b> &nbsp;|&nbsp;
  📦 <b>{sel_row.get('product_name','')}</b> &nbsp;|&nbsp;
  👤 Chercheur : <b>{sel_row.get('researcher_first_name','')}</b>
</div>""", unsafe_allow_html=True)

        # Messages
        msgs = get_chat_messages(sel_req_id)
        r_name = sel_row.get("researcher_first_name", "Chercheur") or "Chercheur"

        if msgs.empty:
            st.markdown("""
            <div style="text-align:center;padding:30px;color:#94a3b8;">
                <div style="font-size:36px;">👋</div>
                <p>Conversation ouverte — envoyez le premier message !</p>
            </div>""", unsafe_allow_html=True)
        else:
            bubbles_html = ""
            for _, m in msgs.iterrows():
                is_me  = m["sender_id"] == owner_id
                side   = "right" if is_me else "left"
                av_cls = "av-me" if is_me else "av-them"
                label  = "Vous" if is_me else r_name
                init   = "M" if is_me else r_name[0].upper()
                ts     = str(m["created_at"])[-19:-3] if len(str(m["created_at"])) >= 19 else str(m["created_at"])
                align  = "text-align:right;" if is_me else ""

                bubbles_html += f"""
<div class="bwrap {side}">
  <div class="av {av_cls}">{init}</div>
  <div>
    <div style="font-size:11px;color:#94a3b8;margin-bottom:3px;{align}">{label}</div>
    <div class="bubble {side}">
      {m['message']}
      <div class="bts">{ts}</div>
    </div>
  </div>
</div>"""
            st.markdown(f'<div class="chat-box">{bubbles_html}</div>', unsafe_allow_html=True)

        # Zone de saisie
        col_txt, col_btn = st.columns([5, 1])
        with col_txt:
            owner_msg = st.text_input(
                "Message",
                placeholder="Écrire un message…",
                key=f"owner_msg_input_{sel_req_id}",
                label_visibility="collapsed",
            )
        with col_btn:
            if st.button("➤ Envoyer", key=f"owner_send_{sel_req_id}", use_container_width=True, type="primary"):
                if owner_msg and owner_msg.strip():
                    ok, fb = send_chat_message(sel_req_id, owner_id, "owner", owner_msg)
                    if ok:
                        st.rerun()
                    else:
                        st.warning(fb)
                else:
                    st.warning("Message vide.")

        col_refresh, _ = st.columns([1, 5])
        with col_refresh:
            if st.button("🔄 Rafraîchir", key=f"refresh_owner_{sel_req_id}"):
                st.rerun()

# ─── Onglet 3 : Historique ─────────────────────────────────────────────────
with tab_history:
    if all_requests.empty:
        st.info("Aucun historique disponible.")
    else:
        status_map = {
            REQUEST_PENDING:  "⏳ En attente",
            REQUEST_ACCEPTED: "✅ Acceptée",
            "rejected":       "❌ Refusée",
        }
        hist = all_requests.copy()
        hist["Statut"]    = hist["status"].map(status_map).fillna(hist["status"])
        hist["Entrepôt"]  = hist.get("warehouse_name", hist.get("warehouse_id", "—"))
        hist["Adresse"]   = hist.get("warehouse_address", "")
        hist["Chercheur"] = hist["researcher_first_name"]
        hist["Produit"]   = hist["product_name"]
        hist["Date"]      = hist["created_at"]
        st.dataframe(
            hist[["Entrepôt", "Adresse", "Chercheur", "Produit", "Statut", "Date"]],
            use_container_width=True,
            hide_index=True,
        )

st.write("")
if st.button("🚪 Se déconnecter", key="logout_msg"):
    st.session_state.clear()
    st.switch_page("app.py")
