import io

filepath = 'pages/8_Interface_Proprietaire.py'

with io.open(filepath, encoding='utf-8') as f:
    lines = f.readlines()

content = ''.join(lines)

# 1. Changer le bouton goto_msg pour naviguer vers la page messagerie
old_btn = (
    '    if st.button("\U0001f4ac Ouvrir la messagerie \u279c", key="goto_msg", use_container_width=True, type="primary"):\n'
    '        st.session_state["jump_to_messaging"] = True\n'
    '        st.rerun()\n'
)
new_btn = (
    '    if st.button("\U0001f4ac Ouvrir la messagerie \u279c", key="goto_msg", use_container_width=True, type="primary"):\n'
    '        st.switch_page("pages/10_Messagerie_Proprietaire.py")\n'
)

if old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    print("OK: bouton goto_msg mis a jour")
else:
    # essayer variante
    old_btn2 = (
        '    if st.button("\U0001f4ac Ouvrir la messagerie \u279c", key="goto_msg", use_container_width=True, type="primary"):\n'
        '        st.session_state["jump_to_messaging"] = True\n'
        '        st.rerun()\n'
    )
    print(f"WARN: bouton non trouve, cherche pattern...")
    idx = content.find('goto_msg')
    if idx >= 0:
        print(repr(content[idx-10:idx+200]))

# 2. Supprimer tout le bloc conditionnel "if st.session_state.get('show_messaging', False)"
# Trouver debut et fin de ce bloc
show_start = content.find('\nif st.session_state.get("show_messaging", False):\n')
if show_start < 0:
    show_start = content.find('\nif st.session_state.get("show_messaging",False):\n')
    
# Aussi supprimer le bloc "jump_to_messaging" et le divider avant
jump_block = '\n# Gestion du bouton messagerie\nif st.session_state.get("jump_to_messaging"):\n    st.session_state["jump_to_messaging"] = False\n    st.session_state["show_messaging"] = True\n\n'

if jump_block in content:
    content = content.replace(jump_block, '\n', 1)
    print("OK: bloc jump_to_messaging supprime")

if show_start >= 0:
    # Trouver la fin du bloc (tout jusqu'a la fin du fichier ou le logout)
    # Le bloc "if show_messaging" va jusqu'a la fin
    content = content[:show_start] + '\n'
    print(f"OK: bloc show_messaging supprime a partir de l'index {show_start}")

    # Rajouter juste le bouton logout et caption a la fin
    content = content.rstrip() + '\n\nst.write("")\nif st.button("\U0001f6aa Se d\u00e9connecter", key="logout_btn"):\n    st.session_state.clear()\n    st.switch_page("pages/1_Login.py")\nst.write("")\nst.caption("OptiStock \u2014 Warehouse Monitoring Dashboard")\n'
    print("OK: logout rajoute")
else:
    print("WARN: bloc show_messaging non trouve")

with io.open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fichier sauvegarde.")
