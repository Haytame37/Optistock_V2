import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'optistock.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print('=== TOUS LES UTILISATEURS (actifs ET inactifs) ===')
cursor.execute('SELECT user_id, email, role, is_active, created_at FROM users ORDER BY user_id')
rows = cursor.fetchall()
for r in rows:
    status = 'ACTIF' if r[3] == 1 else 'SUSPENDU/INACTIF'
    print(f'  ID={r[0]} | {r[1]} | role={r[2]} | {status} | cree={r[4]}')

print(f'\nTotal: {len(rows)} utilisateurs')

print('\n=== sqlite_sequence (compteur AUTOINCREMENT) ===')
cursor.execute('SELECT * FROM sqlite_sequence')
for r in cursor.fetchall():
    print(f'  table={r[0]} | seq={r[1]}')

conn.close()
