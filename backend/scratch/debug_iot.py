import requests
import json

DEVICE_ID = "506b1a20-5053-11f1-aa03-0f0d95b4aecc"
url = f"https://demo.thingsboard.io/api/plugins/telemetry/DEVICE/{DEVICE_ID}/values/timeseries"

print(f"[*] Test de connexion vers ThingsBoard ({DEVICE_ID})...")
try:
    response = requests.get(url, timeout=10)
    print(f"[*] Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("[*] Données reçues de ThingsBoard :")
        print(json.dumps(data, indent=2))
        
        # Vérification des clés
        keys = data.keys()
        print(f"[*] Clés disponibles : {list(keys)}")
    else:
        print(f"[!] Erreur : ThingsBoard a répondu {response.status_code}")
        if response.status_code == 401:
            print("[!] CONSEIL : Votre appareil n'est probablement pas en mode 'PUBLIC'.")
            
except Exception as e:
    print(f"[!] Erreur de connexion : {e}")
