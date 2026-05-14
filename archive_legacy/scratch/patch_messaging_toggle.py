import io

filepath = 'pages/8_Interface_Proprietaire.py'

with io.open(filepath, encoding='utf-8') as f:
    lines = f.readlines()

# Trouver la ligne du divider avant le CSS messagerie (ligne ~233)
# et la ligne du commentaire # CSS Messagerie Premium (ligne ~240)
css_start = None
for i, l in enumerate(lines):
    if '# CSS Messagerie Premium' in l:
        css_start = i
        break

if css_start is None:
    print("ERREUR: CSS Messagerie Premium non trouve")
    exit(1)

# Remonter pour trouver le divider avant
divider_before = css_start
for i in range(css_start - 1, max(0, css_start - 10), -1):
    if lines[i].strip() == 'st.divider()':
        divider_before = i
        break

print(f"divider_before={divider_before+1}, css_start={css_start+1}")

# 1. Remplacer le bloc "jump_to_messaging" par le toggle show_messaging
old_jump = (
    '# Gestion du scroll automatique vers la messagerie\n'
    'if st.session_state.get("jump_to_messaging"):\n'
    '    st.session_state["jump_to_messaging"] = False\n'
    '    st.markdown(\'<script>window.scrollTo(0, document.body.scrollHeight)</script>\', unsafe_allow_html=True)\n'
)
new_jump = (
    '# Gestion du bouton messagerie\n'
    'if st.session_state.get("jump_to_messaging"):\n'
    '    st.session_state["jump_to_messaging"] = False\n'
    '    st.session_state["show_messaging"] = True\n'
    '\n'
)

content = ''.join(lines)
if old_jump in content:
    content = content.replace(old_jump, new_jump, 1)
    print("OK: jump_to_messaging remplace")
else:
    print("WARN: jump_to_messaging non trouve exactement, recherche approx...")
    # chercher ligne par ligne
    for i, l in enumerate(lines):
        if 'jump_to_messaging' in l and 'False' in l:
            print(f"  Trouve approx. ligne {i+1}: {repr(l)}")

# 2. Entourer tout le bloc messagerie (depuis le divider) avec if show_messaging:
lines2 = content.splitlines(keepends=True)

# Trouver la nouvelle position du divider avant CSS
divider_idx = None
css_idx = None
for i, l in enumerate(lines2):
    if '# Gestion du bouton messagerie' in l:
        # le divider est juste avant
        for j in range(i-1, max(0, i-5), -1):
            if lines2[j].strip() == 'st.divider()':
                divider_idx = j
                break
    if '# CSS Messagerie Premium' in l:
        css_idx = i

print(f"divider_idx={divider_idx+1 if divider_idx else None}, css_idx={css_idx+1 if css_idx else None}")

if divider_idx is not None and css_idx is not None:
    # Inserer "if st.session_state.get('show_messaging', False):" avant le divider
    # et indenter tout ce qui suit jusqu'a la fin
    indent = '    '
    
    # Trouver la fin du fichier (ou le bouton logout)
    end_idx = len(lines2)
    for i in range(len(lines2)-1, css_idx, -1):
        if "Se d\u00e9connecter" in lines2[i] or 'logout_btn' in lines2[i]:
            # Inclure jusqu'a la fin
            break
    
    # Remplacer le divider par: if show_messaging + divider indenté + reste indenté
    before = lines2[:divider_idx]
    messaging_block = lines2[divider_idx:]
    
    # Indenter le bloc messagerie
    indented = []
    for l in messaging_block:
        if l.strip() == '':
            indented.append('\n')
        else:
            indented.append(indent + l)
    
    # Ajouter le wrapper
    wrapper_open = [
        '\n',
        'if st.session_state.get("show_messaging", False):\n',
        f'{indent}col_close, _ = st.columns([1, 5])\n',
        f'{indent}with col_close:\n',
        f'{indent}    if st.button("\u274c Fermer la messagerie", key="close_msg"):\n',
        f'{indent}        st.session_state["show_messaging"] = False\n',
        f'{indent}        st.rerun()\n',
        '\n',
    ]
    
    new_lines = before + wrapper_open + indented
    content2 = ''.join(new_lines)
    
    with io.open(filepath, 'w', encoding='utf-8') as f:
        f.write(content2)
    print("Fichier mis a jour avec succes.")
else:
    # Juste sauvegarder les changements step 1
    with io.open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sauvegarde partielle (step 1 seulement).")
