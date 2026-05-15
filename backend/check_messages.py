import sqlite3
import os
import pandas as pd

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "database", "optistock.db"))

def check():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("--- DEMANDES POUR LE CHERCHEUR ID 1 (Najat) ---")
    cursor.execute("SELECT * FROM contact_requests WHERE researcher_id = 1")
    rows = cursor.fetchall()
    for r in rows:
        print(dict(r))
        
    print("\n--- MESSAGES DE CHAT POUR CES DEMANDES ---")
    for r in rows:
        rid = r['request_id']
        cursor.execute("SELECT * FROM chat_messages WHERE request_id = ?", (rid,))
        chats = cursor.fetchall()
        print(f"Chat for {rid}: {len(chats)} messages")
        for c in chats:
            print(f"  [{c['sender_role']}] {c['message'][:30]}...")

    conn.close()

if __name__ == "__main__":
    check()
