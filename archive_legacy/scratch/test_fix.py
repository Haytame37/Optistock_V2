import sys
sys.path.insert(0, '.')
from core.auth import create_user
import sqlite3
from utils.db import DB_PATH

# Test 1: essayer de re-creer un compte suspendu (salah@optistock.com est is_active=0)
result = create_user('researcher', 'Salah', 'Test', 'salah@optistock.com', 'Test@1234')
print("Test re-inscription email suspendu:", "OK - Compte reactivé" if result else "ECHEC")

# Test 2: email inexistant
result2 = create_user('owner', 'Nouveau', 'User', 'nouveau_test_diag@test.com', 'Test@1234')
print("Test nouvel email:", "OK - Compte cree" if result2 else "ECHEC")

# Nettoyage
conn = sqlite3.connect(DB_PATH)
conn.execute("DELETE FROM users WHERE email = 'nouveau_test_diag@test.com'")
conn.execute("UPDATE users SET is_active=0, first_name='salah', last_name='test' WHERE email='salah@optistock.com'")
conn.commit()
conn.close()
print("Nettoyage effectue. Tests termines.")
