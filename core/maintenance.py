import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from utils.db import DB_PATH, execute_query, load_sql_to_dataframe
from utils.email_utils import send_suspension_email

def process_inactive_users(current_user_id=None):
    """
    Vérifie et suspend les comptes créés depuis plus de 2 minutes
    s'ils n'ont effectué aucune action.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    suspended_count = 0
    suspended_emails = []
    
    try:
        # 1. Identifier les candidats (actifs, créés il y a > 2 min)
        query = """
        SELECT user_id, email, role, created_at 
        FROM users 
        WHERE is_active = 1 
        AND role IN ('owner', 'researcher')
        AND created_at <= datetime('now', '-2 minutes')
        """
        df_candidates = pd.read_sql_query(query, conn)
        
        for _, user in df_candidates.iterrows():
            user_id = user['user_id']
            role = user['role']
            email = user['email']
            
            # Ne jamais suspendre l'utilisateur en cours
            if current_user_id and user_id == current_user_id:
                continue
            
            has_action = False
            
            if role == 'owner':
                cursor.execute("SELECT COUNT(*) FROM warehouses WHERE owner_id = ?", (user_id,))
                if cursor.fetchone()[0] > 0:
                    has_action = True
            
            elif role == 'researcher':
                cursor.execute("SELECT COUNT(*) FROM delivery_points WHERE researcher_id = ?", (user_id,))
                if cursor.fetchone()[0] > 0:
                    has_action = True
                    
            elif role == 'admin':
                has_action = True # Les admins ne sont pas suspendus
            
            # 2. Suspendre si aucune action
            if not has_action:
                cursor.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))
                suspended_count += 1
                suspended_emails.append(email)
                
                # Envoi de l'email réel (ou simulation si non configuré)
                send_suspension_email(email, reason="Inactivite apres 2 minutes")
        
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de la maintenance des utilisateurs : {e}")
    finally:
        conn.close()
        
    return suspended_count, suspended_emails
def reorder_user_ids():
    """
    Réordonne tous les user_id de 1 à N pour combler les trous après une suppression.
    Met à jour toutes les tables liées (warehouses, delivery_points, reservations, etc.).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Récupérer tous les utilisateurs triés par leur ID actuel
        cursor.execute("SELECT * FROM users ORDER BY user_id")
        users = cursor.fetchall()
        
        # Obtenir les noms des colonnes
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        user_id_index = columns.index("user_id")
        
        # 2. Créer une table de correspondance (Ancien ID -> Nouvel ID)
        mapping = {}
        for i, user in enumerate(users):
            mapping[user[user_id_index]] = i + 1
            
        # 3. Désactiver les contraintes de clés étrangères temporairement pour les mises à jour
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # 4. Mettre à jour les tables de référence
        for old_id, new_id in mapping.items():
            if old_id == new_id: continue
            
            cursor.execute("UPDATE warehouses SET owner_id = ? WHERE owner_id = ?", (new_id, old_id))
            cursor.execute("UPDATE delivery_points SET researcher_id = ? WHERE researcher_id = ?", (new_id, old_id))
            cursor.execute("UPDATE my_warehouse SET researcher_id = ? WHERE researcher_id = ?", (new_id, old_id))
            cursor.execute("UPDATE reservations SET researcher_id = ? WHERE researcher_id = ?", (new_id, old_id))
            
        # 5. Remplacer la table users
        # On vide la table et on réinsère avec les nouveaux IDs
        cursor.execute("DELETE FROM users")
        for old_id, new_id in mapping.items():
            # Trouver l'utilisateur correspondant dans la liste récupérée
            user_data = next(u for u in users if u[user_id_index] == old_id)
            user_list = list(user_data)
            user_list[user_id_index] = new_id
            
            placeholders = ",".join(["?"] * len(user_list))
            cursor.execute(f"INSERT INTO users ({','.join(columns)}) VALUES ({placeholders})", user_list)
            
        # 6. Réinitialiser le compteur AUTOINCREMENT
        cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'users'", (len(users),))
        
        # 7. Réactiver les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors du reordonnancement des IDs : {e}")
        return False
    finally:
        conn.close()
