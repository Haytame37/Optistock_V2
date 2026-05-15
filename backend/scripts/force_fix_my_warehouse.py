import sqlite3

def force_fix_my_warehouse():
    conn = sqlite3.connect('backend/database/optistock.db')
    cursor = conn.cursor()
    try:
        # On ajoute explicitement la colonne iot_token à la table my_warehouse
        cursor.execute("ALTER TABLE my_warehouse ADD COLUMN iot_token TEXT")
        print("Colonne 'iot_token' ajoutée avec succès à la table 'my_warehouse'.")
    except sqlite3.OperationalError:
        print("La colonne 'iot_token' existe déjà dans 'my_warehouse'.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    force_fix_my_warehouse()
