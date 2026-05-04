import sqlite3
import hashlib
import os
from utils.db import DB_PATH
from utils.helpers import get_current_time

def _connect():
    """Connexion SQLite avec WAL et timeout pour éviter les verrous."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(role, first_name, last_name, email, password):
    """Crée un nouveau compte utilisateur.
    Plusieurs comptes peuvent partager le même email (rôles différents).
    Retourne True si la création a réussi, False sinon.
    """
    conn = None
    try:
        conn = _connect()
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
    """Authentifie un utilisateur par email + mot de passe.
    
    Retourne :
    - None  si aucun compte ne correspond
    - dict  si un seul compte actif correspond
    - list  si plusieurs comptes actifs partagent le même email
              (le login affichera un sélecteur de rôle)
    """
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, role, first_name, last_name, is_active "
            "FROM users WHERE email = ? AND password_hash = ? AND is_active = 1 "
            "ORDER BY created_at DESC",
            (email, hash_password(password))
        )
        rows = cursor.fetchall()
        if not rows:
            return None
        accounts = [
            {"user_id": r[0], "role": r[1], "first_name": r[2],
             "last_name": r[3], "is_active": r[4]}
            for r in rows
        ]
        return accounts[0] if len(accounts) == 1 else accounts
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None
    finally:
        if conn:
            conn.close()

import uuid

def add_warehouse(owner_id, name, address, volume_m3, latitude, longitude):
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        
        # Génération d'un ID de format ENT001, ENT002...
        cursor.execute("SELECT MAX(CAST(SUBSTR(warehouse_id, 4) AS INTEGER)) FROM warehouses WHERE warehouse_id LIKE 'ENT%'")
        max_id = cursor.fetchone()[0]
        next_val = (max_id or 0) + 1
        warehouse_id = f"ENT{next_val:03d}"
        now_str = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO warehouses (warehouse_id, owner_id, name, address, volume_m3, latitude, longitude, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'available', ?)
        ''', (warehouse_id, owner_id, name, address, volume_m3, latitude, longitude, now_str))
        conn.commit()
        return warehouse_id
    except Exception as e:
        print(f"Error adding warehouse: {e}")
        return None
    finally:
        if conn:
            conn.close()

def delete_warehouse(warehouse_id):
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warehouses WHERE warehouse_id = ?", (warehouse_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting warehouse: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_warehouse_by_id(warehouse_id):
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name, address, volume_m3, latitude, longitude FROM warehouses WHERE warehouse_id = ?", (warehouse_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching warehouse: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_warehouse(warehouse_id, name, address, volume_m3, latitude, longitude):
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        now_str = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            UPDATE warehouses 
            SET name = ?, address = ?, volume_m3 = ?, latitude = ?, longitude = ?, updated_at = ?
            WHERE warehouse_id = ?
        """, (name, address, volume_m3, latitude, longitude, now_str, warehouse_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating warehouse: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_warehouses_by_owner(owner_id):
    """Récupère tous les entrepôts appartenant à un propriétaire spécifique."""
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute("SELECT warehouse_id, name, address, volume_m3, latitude, longitude, status FROM warehouses WHERE owner_id = ?", (owner_id,))
        rows = cursor.fetchall()
        
        result = []
        for r in rows:
            st_val = "Disponible"
            if r[6] == "unavailable": st_val = "Non disponible"
            
            result.append({
                "id": r[0],
                "name": r[1],
                "address": r[2] if r[2] else "Aucune adresse",
                "volume": r[3],
                "lat": r[4],
                "lon": r[5],
                "gps": f"{r[4]}° N, {r[5]}° E",
                "status": st_val
            })
        return result
    except Exception as e:
        print(f"Error fetching warehouses: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_recent_warehouses_by_owner(owner_id, limit=3):
    """Récupère les entrepôts les plus récents pour un propriétaire."""
    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        # On trie par warehouse_id décroissant
        cursor.execute("""
            SELECT warehouse_id, name, address, latitude, longitude, status 
            FROM warehouses 
            WHERE owner_id = ? 
            ORDER BY warehouse_id DESC 
            LIMIT ?
        """, (owner_id, limit))
        rows = cursor.fetchall()
        
        result = []
        for r in rows:
            st_val = "Disponible"
            if r[5] == "unavailable": st_val = "Non disponible"
            
            result.append({
                "id": r[0],
                "name": r[1],
                "address": r[2] if r[2] else "Aucune adresse",
                "lat": r[3],
                "lon": r[4],
                "gps": f"{r[3]}° N, {r[4]}° E",
                "status": st_val
            })
        return result
    except Exception as e:
        print(f"Error fetching recent warehouses: {e}")
        return []
    finally:
        if conn:
            conn.close()


def import_iot_csv(warehouse_id, df):
    """
    Importe les données environnementales d'un DataFrame CSV dans iot_readings.
    Le CSV doit contenir une colonne de date/heure et au moins une colonne
    de température ou d'humidité.
    Colonnes acceptées (case-insensitive) :
        date/heure   -> recorded_at
        temp_1/temperature_1/t1 -> temp_sensor_1
        temp_2/temperature_2/t2 -> temp_sensor_2
        temp_3/temperature_3/t3 -> temp_sensor_3
        hum_1/humidite_1/h1    -> hum_sensor_1
        hum_2/humidite_2/h2    -> hum_sensor_2
        hum_3/humidite_3/h3    -> hum_sensor_3
    """
    import pandas as pd

    # Normalisation des noms de colonnes
    df.columns = [c.strip().lower() for c in df.columns]
    
    MAPPING = {
        'recorded_at':  ['date', 'datetime', 'heure', 'timestamp', 'time', 'recorded_at'],
        'temp_sensor_1': ['temp_1', 'temperature_1', 't1', 'temp1', 'temperature1'],
        'temp_sensor_2': ['temp_2', 'temperature_2', 't2', 'temp2', 'temperature2'],
        'temp_sensor_3': ['temp_3', 'temperature_3', 't3', 'temp3', 'temperature3'],
        'hum_sensor_1':  ['hum_1', 'humidite_1', 'humidity_1', 'h1', 'hum1'],
        'hum_sensor_2':  ['hum_2', 'humidite_2', 'humidity_2', 'h2', 'hum2'],
        'hum_sensor_3':  ['hum_3', 'humidite_3', 'humidity_3', 'h3', 'hum3'],
    }

    renamed = {}
    for target_col, aliases in MAPPING.items():
        for alias in aliases:
            if alias in df.columns and target_col not in renamed:
                renamed[alias] = target_col
                break

    df = df.rename(columns=renamed)

    if 'recorded_at' not in df.columns:
        return False, "❌ Colonne date/heure introuvable. Vérifiez que votre CSV contient une colonne 'date', 'datetime' ou 'timestamp'."

    sensor_cols = ['temp_sensor_1', 'temp_sensor_2', 'temp_sensor_3',
                   'hum_sensor_1',  'hum_sensor_2',  'hum_sensor_3']

    # Ajouter les colonnes manquantes avec None
    for col in sensor_cols:
        if col not in df.columns:
            df[col] = None

    # Nettoyage
    df['recorded_at'] = pd.to_datetime(df['recorded_at'], errors='coerce')
    df = df.dropna(subset=['recorded_at'])
    df['recorded_at'] = df['recorded_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

    rows = df[['recorded_at'] + sensor_cols].values.tolist()

    conn = None
    try:
        conn = _connect()
        cursor = conn.cursor()
        # Supprimer les anciennes données pour éviter les doublons
        cursor.execute("DELETE FROM iot_readings WHERE warehouse_id = ?", (warehouse_id,))
        cursor.executemany("""
            INSERT INTO iot_readings 
                (warehouse_id, recorded_at, temp_sensor_1, temp_sensor_2, temp_sensor_3,
                 hum_sensor_1, hum_sensor_2, hum_sensor_3)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(warehouse_id, *r) for r in rows])
        conn.commit()
        return True, f"✅ {len(rows)} lectures IoT importées avec succès."
    except Exception as e:
        print(f"Error importing IoT CSV: {e}")
        return False, f"❌ Erreur lors de l'import : {e}"
    finally:
        if conn:
            conn.close()

