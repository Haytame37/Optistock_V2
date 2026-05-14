import sys
sys.path.insert(0, '.')
from core.auth import create_user, authenticate_user
from utils.db import DB_PATH
import sqlite3

print("=== TEST MULTI-COMPTES PAR EMAIL ===\n")

TEST_EMAIL = "multitest@optistock.com"
TEST_PWD   = "Test@1234Abc!"

# Creer 2 comptes avec le meme email
r1 = create_user("owner",      "Alice", "Dupont", TEST_EMAIL, TEST_PWD)
r2 = create_user("researcher", "Alice", "Dupont", TEST_EMAIL, TEST_PWD)

print(f"Compte 1 (owner)      cree : {'OK' if r1 else 'ECHEC'}")
print(f"Compte 2 (researcher) cree : {'OK' if r2 else 'ECHEC'}")

# Authentification
result = authenticate_user(TEST_EMAIL, TEST_PWD)
if isinstance(result, list):
    print(f"\nauthenticate_user retourne {len(result)} comptes (liste) -> OK")
    for acc in result:
        print(f"  - role={acc['role']} | id={acc['user_id']}")
elif isinstance(result, dict):
    print(f"\nauthenticate_user retourne 1 compte (dict): role={result['role']}")
else:
    print("\nauthenticate_user retourne None -> ECHEC")

# Nettoyage
conn = sqlite3.connect(DB_PATH, timeout=30)
conn.execute("PRAGMA journal_mode = WAL")
conn.execute(f"DELETE FROM users WHERE email = '{TEST_EMAIL}'")
conn.commit()
conn.close()
print("\nNettoyage effectue. Test termine.")
