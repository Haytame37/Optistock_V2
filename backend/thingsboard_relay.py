import serial
import requests
import json
import time

# --- CONFIGURATION ---
# Le port COM2 doit être lié au COM1 (utilisé par Proteus) via VSPD ou com0com
SERIAL_PORT = 'COM2' 
BAUD_RATE = 9600

# Informations de votre compte ThingsBoard
THINGSBOARD_HOST = 'demo.thingsboard.io' 
ACCESS_TOKEN = 'A5nfCs8VOOzz97F0sD4h' 

# URL de l'API Telemetry de ThingsBoard
THINGSBOARD_URL = f'https://{THINGSBOARD_HOST}/api/v1/{ACCESS_TOKEN}/telemetry'

def run_relay():
    print("--- RELAIS IOT OPTISTOCK (VERSION CLIENT) ---")
    print(f"[*] Démarrage du relais sur {SERIAL_PORT}...")
    
    try:
        # Initialisation de la connexion série
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[OK] Connecté au port {SERIAL_PORT}. En attente de données de Proteus...")
        
        while True:
            if ser.in_waiting > 0:
                # Lecture de la ligne envoyée par Proteus
                line = ser.readline().decode('utf-8').strip()
                
                if line:
                    print(f"[>] Reçu de Proteus: {line}")
                    
                    try:
                        # On vérifie si c'est du JSON valide
                        data = json.loads(line)
                        
                        # Envoi vers ThingsBoard
                        response = requests.post(THINGSBOARD_URL, json=data, timeout=5)
                        
                        if response.status_code == 200:
                            print(f"    [OK] Envoyé à ThingsBoard avec succès.")
                        else:
                            print(f"    [!] Erreur ThingsBoard: {response.status_code} - {response.text}")
                            
                    except json.JSONDecodeError:
                        print(f"    [!] Erreur: Les données reçues ne sont pas au format JSON valide.")
                    except Exception as e:
                        print(f"    [!] Erreur lors de l'envoi: {e}")
            
            time.sleep(0.1) # Petite pause pour ne pas saturer le CPU

    except serial.SerialException as e:
        print(f"[ERROR] Impossible d'ouvrir le port {SERIAL_PORT}. Vérifiez s'il est déjà utilisé ou s'il existe.")
        print(f"Détails: {e}")
    except KeyboardInterrupt:
        print("\n[*] Arrêt du script par l'utilisateur.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("[*] Port série fermé.")

if __name__ == "__main__":
    run_relay()
