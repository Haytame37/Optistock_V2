import requests
import json
import os
from dotenv import load_dotenv

# Charger le .env
load_dotenv("backend/.env")

username = os.getenv("THINGSBOARD_USERNAME")
password = os.getenv("THINGSBOARD_PASSWORD")

print(f"[*] Tentative de connexion pour : {username}")

try:
    login_url = "https://demo.thingsboard.io/api/auth/login"
    login_resp = requests.post(
        login_url,
        json={"username": username, "password": password},
        timeout=10
    )
    print(f"[*] Status Code Login: {login_resp.status_code}")
    
    if login_resp.status_code == 200:
        token = login_resp.json().get("token")
        print("[*] Connexion RÉUSSIE !")
        
        # Test de lecture
        DEVICE_ID = "506b1a20-5053-11f1-aa03-0f0d95b4aecc"
        keys = "ZoneA_Temp,ZoneA_Hum,ZoneB_Temp,ZoneB_Hum,ZoneC_Temp,ZoneC_Hum"
        url = f"https://demo.thingsboard.io/api/plugins/telemetry/DEVICE/{DEVICE_ID}/values/timeseries?keys={keys}"
        headers = {"X-Authorization": f"Bearer {token}"}
        
        data_resp = requests.get(url, headers=headers, timeout=10)
        print(f"[*] Status Code Données: {data_resp.status_code}")
        print("[*] Données reçues :")
        print(json.dumps(data_resp.json(), indent=2))
    else:
        print(f"[!] Erreur de connexion : {login_resp.text}")
            
except Exception as e:
    print(f"[!] Erreur : {e}")
