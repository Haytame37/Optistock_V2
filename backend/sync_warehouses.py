import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "database", "optistock.db"))

def sync_statuses():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Synchronisation des statuts des entrepôts...")
    
    # 1. Marquer comme 'rented' tous ceux qui ont une réservation confirmée
    cursor.execute("""
        UPDATE warehouses 
        SET status = 'rented' 
        WHERE warehouse_id IN (
            SELECT warehouse_id FROM reservations WHERE status = 'confirmed'
        )
    """)
    rented_count = cursor.rowcount
    
    # 2. S'assurer que les autres (qui ne sont pas en maintenance) sont 'available'
    cursor.execute("""
        UPDATE warehouses 
        SET status = 'available' 
        WHERE (status IS NULL OR status = '')
          AND warehouse_id NOT IN (
            SELECT warehouse_id FROM reservations WHERE status = 'confirmed'
          )
    """)
    available_count = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"Terminé ! {rented_count} entrepôts marqués comme Loués, {available_count} initialisés comme Disponibles.")

if __name__ == "__main__":
    sync_statuses()
