import sqlite3
import pandas as pd

try:
    conn = sqlite3.connect('database/optistock.db')
    query = "SELECT * FROM users WHERE email='ahmed@gmail.com'"
    df = pd.read_sql_query(query, conn)
    if not df.empty:
        for index, row in df.iterrows():
            print(row.to_dict())
    else:
        print("No user found with email ahmed@gmail.com")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
