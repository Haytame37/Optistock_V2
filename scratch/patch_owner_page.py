import io

filepath = 'pages/8_Interface_Proprietaire.py'

with io.open(filepath, encoding='utf-8') as f:
    lines = f.readlines()

# Trouver les lignes a remplacer
start = None
end = None
for i, l in enumerate(lines):
    if 'st.subheader("Primary Actions")' in l:
        start = i
    if start and i > start and l.strip().startswith('if st.button("D') and 'add' in l:
        end = i + 2  # inclure la ligne switch_page
        break

if start is None or end is None:
    print(f"start={start}, end={end} - lignes non trouvees")
else:
    print(f"Remplacement lignes {start+1} a {end+1}")
    new_block = [
        'st.subheader("Actions principales")\n',
        '\n',
        'col1, col2, col3 = st.columns(3)\n',
        '\n',
        'with col1:\n',
        '    st.markdown("""\n',
        '    <div class="action-card">\n',
        '        <h3 style="color:#00457f;">\U0001f4e6 G\u00e9rer les entrep\u00f4ts</h3>\n',
        '        <p class="small">\n',
        '        Visualisez, modifiez et surveillez l\u2019\u00e9tat de vos unit\u00e9s de stockage.\n',
        '        </p>\n',
        '    </div>\n',
        '    """, unsafe_allow_html=True)\n',
        '    if st.button("Acc\u00e9der \u00e0 la liste \u279c", key="manage", use_container_width=True):\n',
        '        st.switch_page("pages/5_Liste_Entrepots.py")\n',
        '\n',
        'with col2:\n',
        '    st.markdown("""\n',
        '    <div class="action-card">\n',
        '        <h3 style="color:#9a4600;">\u2795 Ajouter un entrep\u00f4t</h3>\n',
        '        <p class="small">\n',
        '        Enregistrez une nouvelle unit\u00e9 et configurez ses capteurs IoT.\n',
        '        </p>\n',
        '    </div>\n',
        '    """, unsafe_allow_html=True)\n',
        '    if st.button("D\u00e9marrer la configuration \u279c", key="add", use_container_width=True):\n',
        '        st.switch_page("pages/6_Ajout_Entrepot.py")\n',
        '\n',
        'with col3:\n',
        '    try:\n',
        '        _pq = get_owner_requests(owner_id)\n',
        '        _pending_n = len(_pq[_pq["status"] == REQUEST_PENDING]) if not _pq.empty else 0\n',
        '    except Exception:\n',
        '        _pending_n = 0\n',
        '    _badge = (\n',
        '        f\'<span style="background:#ef4444;color:#fff;border-radius:999px;\'\n',
        '        f\'padding:1px 8px;font-size:11px;font-weight:700;">{_pending_n}</span>\'\n',
        '        if _pending_n > 0 else ""\n',
        '    )\n',
        '    st.markdown(f"""\n',
        '    <div class="action-card" style="border-color:#2563eb;">\n',
        '        <h3 style="color:#1d4ed8;">\U0001f4ac Messagerie{_badge}</h3>\n',
        '        <p class="small">\n',
        '        G\u00e9rez les demandes des chercheurs et \u00e9changez en temps r\u00e9el avec eux.\n',
        '        </p>\n',
        '    </div>\n',
        '    """, unsafe_allow_html=True)\n',
        '    if st.button("\U0001f4ac Ouvrir la messagerie \u279c", key="goto_msg", use_container_width=True, type="primary"):\n',
        '        st.session_state["jump_to_messaging"] = True\n',
        '        st.rerun()\n',
    ]
    lines = lines[:start] + new_block + lines[end:]
    with io.open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Fichier mis a jour avec succes.")
