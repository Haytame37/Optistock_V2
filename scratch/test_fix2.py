import sys
sys.path.insert(0, '.')
from core.auth import create_user
import sqlite3
from utils.db import DB_PATH

print("=== TEST DU CORRECTIF EMAIL ===\n")

# Afficher l'etat actuel
conn = sqlite3.connect(DB_PATH, timeout=30)
conn.execute("PRAGMA journal_mode = WAL")
cursor = conn.cursor()
cursor.execute("SELECT user_id, email, role, is_active FROM users ORDER BY user_id")
rows = cursor.fetchall()
print("Comptes existants:")
for r in rows:
    status = "ACTIF" if r[3] == 1 else "SUSPENDU"
    print(f"  ID={r[0]} | {r[1]} | {r[2]} | {status}")
conn.close()

print()

# Test 1: email suspendu -> doit reussir
suspended_email = "salah@optistock.com"  # is_active=0 dans la DB
result = create_user("researcher", "Salah", "Reactivé", suspended_email, "Test@1234Abc!")
if result:
    print(f"TEST 1 OK: Re-inscription avec '{suspended_email}' (suspendu) -> REUSSI")
else:
    print(f"TEST 1 ECHEC: Re-inscription avec '{suspended_email}' (suspendu) -> REFUSE")

# Test 2: email actif -> doit echouer
active_email = "najat@optistock.com"  # admin actif
result2 = create_user("owner", "Test", "Doublon", active_email, "Test@1234Abc!")
if not result2:
    print(f"TEST 2 OK: Email actif '{active_email}' -> CORRECTEMENT REFUSE")
else:
    print(f"TEST 2 ECHEC: Email actif '{active_email}' -> aurait du etre refuse")

# Test 3: nouvel email inconnu -> doit reussir
new_email = "test_nouveau_unique_xyz@test.com"
result3 = create_user("owner", "Nouveau", "Compte", new_email, "Test@1234Abc!")
if result3:
    print(f"TEST 3 OK: Nouvel email '{new_email}' -> COMPTE CREE")
else:
    print(f"TEST 3 ECHEC: Nouvel email '{new_email}' -> REFUSE")

# Nettoyage
conn2 = sqlite3.connect(DB_PATH, timeout=30)
conn2.execute("PRAGMA journal_mode = WAL")
conn2.execute(f"DELETE FROM users WHERE email = '{new_email}'")
conn2.execute(f"UPDATE users SET is_active=0, first_name='salah', last_name='test' WHERE email='{suspended_email}'")
conn2.commit()
conn2.close()

print("\nNettoyage effectue. Tous les tests termines.")
