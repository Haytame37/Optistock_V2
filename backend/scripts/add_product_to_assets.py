import sqlite3

def add_product_to_my_warehouse():
    conn = sqlite3.connect('backend/database/optistock.db')
    cursor = conn.cursor()
    try:
        # On ajoute la colonne product_name
        cursor.execute("ALTER TABLE my_warehouse ADD COLUMN product_name TEXT")
        print("Colonne 'product_name' ajoutée à 'my_warehouse'.")
    except sqlite3.OperationalError:
        print("La colonne 'product_name' existe déjà.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_product_to_my_warehouse()
