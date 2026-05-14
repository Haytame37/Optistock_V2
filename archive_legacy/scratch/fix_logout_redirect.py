"""
Change uniquement les redirections APRES deconnexion (session_state.clear())
vers app.py au lieu de 1_Login.py.
Les redirects de securite (non connecte) restent vers 1_Login.py.
"""
import io, os, subprocess, sys

PAGES = [f'pages/{f}' for f in os.listdir('pages') if f.endswith('.py') and not f.startswith('__')]
PAGES.append('app.py')

changed_total = 0

for path in sorted(PAGES):
    with io.open(path, encoding='utf-8') as f:
        content = f.read()

    # Remplacer seulement quand session_state.clear() precede switch_page("pages/1_Login.py")
    # Pattern exact sur deux lignes consecutives
    old = 'st.session_state.clear()\n    st.switch_page("pages/1_Login.py")'
    new = 'st.session_state.clear()\n    st.switch_page("app.py")'

    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [OK] {path}: {count} deconnexion(s) redirigee(s) vers app.py")
        changed_total += count
    else:
        # Chercher variante sans indentation (niveau module)
        old2 = 'st.session_state.clear()\nst.switch_page("pages/1_Login.py")'
        new2 = 'st.session_state.clear()\nst.switch_page("app.py")'
        count2 = content.count(old2)
        if count2 > 0:
            content = content.replace(old2, new2)
            with io.open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] {path}: {count2} deconnexion(s) redirigee(s) vers app.py (niveau module)")
            changed_total += count2

print(f"\nTotal: {changed_total} redirect(s) de deconnexion changes.")

# Verification syntaxe
print("\nVerification syntaxe...")
errors = []
for path in sorted(PAGES):
    r = subprocess.run([sys.executable, '-m', 'py_compile', path], capture_output=True, text=True)
    if r.returncode != 0:
        errors.append(f"  ERR {path}: {r.stderr.strip()[:120]}")
    else:
        print(f"  OK  {path}")

if errors:
    print("\nERREURS:")
    for e in errors:
        print(e)
else:
    print("\nTous les fichiers sont valides.")
