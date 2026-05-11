import sys

with open('pages/9_Interface_Chercheur.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_search_block = False

for i, line in enumerate(lines):
    if line.startswith('if current_view == "search":'):
        new_lines.append(line)
        new_lines.append('    tab1, tab2 = st.tabs(["Module 1: Trouver votre entrepôt", "Module 2: Implémenter votre propre entrepôt"])\n')
        new_lines.append('    with tab2:\n')
        new_lines.append('        st.info("Cette fonctionnalité sera implémentée prochainement.")\n')
        new_lines.append('    with tab1:\n')
        in_search_block = True
        continue
        
    if in_search_block:
        if line.startswith('elif current_view == "mes_entrepots":'):
            in_search_block = False
            new_lines.append(line)
        elif line.strip() == '' or line.startswith('    '):
            if line.strip() == '':
                new_lines.append(line)
            else:
                new_lines.append('    ' + line)
        else:
            in_search_block = False
            new_lines.append(line)
    else:
        new_lines.append(line)

with open('pages/9_Interface_Chercheur.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
