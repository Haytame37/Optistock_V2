"""
Patch automatique: injecte hide_sidebar() dans toutes les pages Streamlit.
"""
import io, os, re

PAGES_DIR = 'pages'
IMPORT_LINE = 'from utils.ui import hide_sidebar\n'
CALL_LINE   = 'hide_sidebar()\n'

pages = [
    f for f in os.listdir(PAGES_DIR)
    if f.endswith('.py') and not f.startswith('__')
]

for page in sorted(pages):
    path = os.path.join(PAGES_DIR, page)
    with io.open(path, encoding='utf-8') as f:
        content = f.read()

    # Verifier si deja present
    if 'hide_sidebar' in content:
        print(f"  [SKIP] {page} - deja present")
        continue

    # Trouver la position apres le dernier import en tete
    # On insere l'import apres le bloc import/from initial
    lines = content.splitlines(keepends=True)

    # Trouver la derniere ligne d'import au debut du fichier
    last_import_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            last_import_idx = i
        elif stripped == '' or stripped.startswith('#'):
            continue  # lignes vides et commentaires: continuer
        elif last_import_idx > 0:
            break  # fin du bloc d'imports

    # Inserer l'import apres le dernier import
    insert_import_at = last_import_idx + 1

    # Trouver le premier appel st.set_page_config ou premier code non-import
    # pour inserer hide_sidebar() juste apres
    call_insert_at = None
    for i in range(insert_import_at, len(lines)):
        stripped = lines[i].strip()
        if 'st.set_page_config' in stripped:
            # Trouver la fin de set_page_config (peut etre multiligne)
            j = i
            while j < len(lines) and ')' not in lines[j]:
                j += 1
            call_insert_at = j + 1
            break

    if call_insert_at is None:
        # Pas de set_page_config: inserer apres les imports
        call_insert_at = insert_import_at + 1

    # Construire le nouveau contenu
    new_lines = (
        lines[:insert_import_at]
        + [IMPORT_LINE]
        + lines[insert_import_at:call_insert_at]
        + [CALL_LINE]
        + lines[call_insert_at:]
    )

    new_content = ''.join(new_lines)
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  [OK]   {page} - hide_sidebar() injecte (import l.{insert_import_at+1}, call l.{call_insert_at+1})")

print("\nTermine.")
