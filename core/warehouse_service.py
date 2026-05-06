import sqlite3
from utils.db import get_db_connection
from utils.helpers import get_current_time

def add_warehouse(owner_id, name, address, volume_m3, latitude, longitude):
    """Ajoute un nouvel entrepôt à la base de données."""
    conn = None
    try:
        conn = get_db_connection()
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
    """Supprime un entrepôt par son ID."""
    conn = None
    try:
        conn = get_db_connection()
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
    """Récupère les détails d'un entrepôt spécifique."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, address, volume_m3, latitude, longitude FROM warehouses WHERE warehouse_id = ?", (warehouse_id,))
        # sqlite3.Row permet l'accès par nom ou index
        return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching warehouse: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_warehouse(warehouse_id, name, address, volume_m3, latitude, longitude):
    """Met à jour les informations d'un entrepôt."""
    conn = None
    try:
        conn = get_db_connection()
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT warehouse_id, name, address, volume_m3, latitude, longitude, status FROM warehouses WHERE owner_id = ?", (owner_id,))
        rows = cursor.fetchall()
        
        result = []
        for r in rows:
            st_val = "Disponible"
            if r['status'] == "unavailable": st_val = "Non disponible"
            
            result.append({
                "id": r['warehouse_id'],
                "name": r['name'],
                "address": r['address'] if r['address'] else "Aucune adresse",
                "volume": r['volume_m3'],
                "lat": r['latitude'],
                "lon": r['longitude'],
                "gps": f"{r['latitude']}° N, {r['longitude']}° E",
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
        conn = get_db_connection()
        cursor = conn.cursor()
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
            if r['status'] == "unavailable": st_val = "Non disponible"
            
            result.append({
                "id": r['warehouse_id'],
                "name": r['name'],
                "address": r['address'] if r['address'] else "Aucune adresse",
                "lat": r['latitude'],
                "lon": r['longitude'],
                "gps": f"{r['latitude']}° N, {r['longitude']}° E",
                "status": st_val
            })
        return result
    except Exception as e:
        print(f"Error fetching recent warehouses: {e}")
        return []
    finally:
        if conn:
            conn.close()
