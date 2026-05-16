import requests
import json
import os
from dotenv import load_dotenv

# Charger le .env
load_dotenv("backend/.env")

DEVICE_ID = "506b1a20-5053-11f1-aa03-0f0d95b4aecc"
url = f"https://demo.thingsboard.io/api/plugins/telemetry/DEVICE/{DEVICE_ID}/values/timeseries"
jwt_token = os.getenv("THINGSBOARD_JWT_TOKEN")

print(f"[*] Test avec JWT Token : {jwt_token[:10]}...")

headers = {}
if jwt_token:
    headers["X-Authorization"] = f"Bearer {jwt_token}"

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"[*] Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("[*] Données brutes reçues :")
        print(json.dumps(data, indent=2))
        
        if not data:
            print("[!] ATTENTION : ThingsBoard ne renvoie aucune donnée pour cet appareil.")
            print("[!] Vérifiez que votre Proteus est bien en train d'envoyer des infos actuellement.")
    else:
        print(f"[!] Erreur ThingsBoard : {response.text}")
            
except Exception as e:
    print(f"[!] Erreur : {e}")
