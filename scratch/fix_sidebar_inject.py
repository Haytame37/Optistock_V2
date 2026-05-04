import io, os

fixes = {
    'pages/10_Messagerie_Proprietaire.py': (
        'from core.messaging import (\nfrom utils.ui import hide_sidebar\n',
        'from core.messaging import (\n'
    ),
    'pages/8_Interface_Proprietaire.py': (
        'from core.messaging import (\nfrom utils.ui import hide_sidebar\n',
        'from core.messaging import (\n'
    ),
    'pages/9_Interface_Chercheur.py': (
        'from core.messaging import (\nfrom utils.ui import hide_sidebar\n',
        'from core.messaging import (\n'
    ),
}

# Pour 1_Login.py: l'import/call est a la mauvaise position (ligne 120)
# On doit le retirer et le remettre au bon endroit (apres set_page_config)

for path, (old, new) in fixes.items():
    with io.open(path, encoding='utf-8') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new, 1)
        # S'assurer que l'import est present quelque part au debut
        if 'from utils.ui import hide_sidebar\n' not in content:
            # Inserer apres la fermeture du import messaging
            idx = content.find(')\n', content.find('from core.messaging import ('))
            if idx >= 0:
                content = content[:idx+2] + 'from utils.ui import hide_sidebar\n' + content[idx+2:]
        print(f"OK: {path}")
    else:
        print(f"WARN pas trouve dans {path}")
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Pour 9_Interface_Chercheur.py, verifier que hide_sidebar est bien la
with io.open('pages/9_Interface_Chercheur.py', encoding='utf-8') as f:
    c = f.read()
if 'from utils.ui import hide_sidebar' not in c:
    # ajouter apres la fermeture du import messaging
    idx = c.find('\nfrom core.auth import')
    if idx < 0:
        idx = c.find('\nimport streamlit')
    c = c[:idx] + '\nfrom utils.ui import hide_sidebar' + c[idx:]
    with io.open('pages/9_Interface_Chercheur.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Fix supplementaire 9_Interface_Chercheur.py")

# Fix 1_Login.py: retirer le hide_sidebar mal place et le remettre proprement
with io.open('pages/1_Login.py', encoding='utf-8') as f:
    lines = f.readlines()

# Retirer les lignes mal placees
clean = [l for l in lines if l.strip() not in ('from utils.ui import hide_sidebar', 'hide_sidebar()')]

# Trouver la fin de set_page_config pour inserer le call
content_clean = ''.join(clean)
# Ajouter import avant set_page_config
idx_sp = content_clean.find('st.set_page_config(')
if idx_sp >= 0:
    # trouver fin du set_page_config
    end_sp = content_clean.find('\n', content_clean.find(')', idx_sp)) + 1
    content_clean = (
        content_clean[:idx_sp]
        + 'from utils.ui import hide_sidebar\n'
        + content_clean[idx_sp:end_sp]
        + 'hide_sidebar()\n'
        + content_clean[end_sp:]
    )
else:
    content_clean = 'from utils.ui import hide_sidebar\nhide_sidebar()\n' + content_clean

with io.open('pages/1_Login.py', 'w', encoding='utf-8') as f:
    f.write(content_clean)
print("OK: pages/1_Login.py")

print("\nVerification syntaxe...")
import subprocess, sys
for path in ['pages/10_Messagerie_Proprietaire.py','pages/1_Login.py','pages/8_Interface_Proprietaire.py','pages/9_Interface_Chercheur.py']:
    r = subprocess.run([sys.executable, '-m', 'py_compile', path], capture_output=True, text=True)
    status = "OK" if r.returncode == 0 else f"ERR: {r.stderr.strip()[:100]}"
    print(f"  {path}: {status}")
