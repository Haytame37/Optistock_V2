import sqlite3
import bcrypt
import os
from utils.db import get_db_connection
from utils.helpers import get_current_time

def hash_password(password):
    """Hache un mot de passe en utilisant bcrypt avec un sel généré automatiquement."""
    # bcrypt.hashpw attend des bytes, on encode donc la chaîne
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    """Vérifie si un mot de passe correspond à son hash bcrypt."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(role, first_name, last_name, email, password):
    """Crée un nouveau compte utilisateur avec un mot de passe sécurisé."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO users (role, first_name, last_name, email, password_hash, is_active, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
            (role, first_name, last_name, email, hash_password(password), now_str, now_str)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        if conn:
            conn.close()

def authenticate_user(email, password):
    """Authentifie un utilisateur en comparant le hash bcrypt en Python."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # On récupère d'abord l'utilisateur par son email
        cursor.execute(
            "SELECT user_id, role, first_name, last_name, password_hash, is_active "
            "FROM users WHERE email = ? AND is_active = 1",
            (email,)
        )
        rows = cursor.fetchall()
        
        if not rows:
            return None
        
        valid_accounts = []
        for r in rows:
            # Vérification sécurisée du mot de passe avec bcrypt
            if check_password(password, r['password_hash']):
                valid_accounts.append({
                    "user_id": r['user_id'],
                    "role": r['role'],
                    "first_name": r['first_name'],
                    "last_name": r['last_name'],
                    "is_active": r['is_active']
                })
        
        if not valid_accounts:
            return None
            
        return valid_accounts[0] if len(valid_accounts) == 1 else valid_accounts
        
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None
    finally:
        if conn:
            conn.close()
