import sqlite3

def add_storage_type():
    conn = sqlite3.connect('backend/database/optistock.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE warehouses ADD COLUMN storage_type TEXT DEFAULT 'standard'")
        print("Colonne 'storage_type' ajoutée.")
        # On met Hub 1 en standard explicitement
        cursor.execute("UPDATE warehouses SET storage_type = 'standard' WHERE warehouse_id = 'ENT001'")
        print("Hub 1 marqué comme 'standard'.")
    except Exception as e:
        print(f"Erreur ou colonne déjà présente : {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_storage_type()
