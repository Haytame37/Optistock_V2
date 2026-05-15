import sqlite3

def check_hub1():
    conn = sqlite3.connect('backend/database/optistock.db')
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(temp_sensor_1), AVG(hum_sensor_1) FROM iot_readings WHERE warehouse_id = "ENT001"')
    res = cursor.fetchone()
    print(f"Hub 1 Avg Temp: {res[0]}°C, Avg Hum: {res[1]}%")
    conn.close()

if __name__ == "__main__":
    check_hub1()
