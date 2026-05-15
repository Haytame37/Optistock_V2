import sqlite3
import pandas as pd
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "optistock.db"))

def get_db_connection():
    """Crée et retourne une connexion à la base de données SQLite.
    
    Utilise le mode WAL (Write-Ahead Logging) pour permettre les accès
    concurrents sans blocage (database is locked) dans l'environnement
    multi-thread de Streamlit.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")   # Évite les verrous en écriture concurrente
    conn.execute("PRAGMA synchronous = NORMAL")  # Bon compromis performance/sécurité
    conn.execute("PRAGMA busy_timeout = 30000")  # Attend 30s avant d'échouer
    # Permet d'accéder aux colonnes via leur nom au lieu d'un index
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=()):
    """Exécute une requête (INSERT, UPDATE, DELETE), commit et retourne True si réussi."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"DB Error: {e}")
        return False
    finally:
        conn.close()

def load_sql_to_dataframe(query, params=()):
    """Exécute une requête SELECT et la charge directement dans un DataFrame Pandas."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()
    return df
