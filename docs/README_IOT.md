# 🛰️ Guide d'Intégration IoT OptiStock (Proteus + ThingsBoard)

Ce guide explique comment connecter votre simulation Proteus à votre compte ThingsBoard Cloud et l'afficher dans votre application.

## 1. Partie Matérielle (Simulation Proteus)

### Code ATmega 2560 (Arduino IDE)
Copiez ce code dans votre IDE Arduino, compilez-le et chargez le fichier `.hex` dans votre ATmega sur Proteus.

```cpp
#include <DHT.h>

// --- Configuration des Capteurs DHT11 ---
#define DHTPIN1 2  // Broche DATA DHT 1
#define DHTPIN2 3  // Broche DATA DHT 2
#define DHTPIN3 4  // Broche DATA DHT 3
#define DHTTYPE DHT11

DHT dht1(DHTPIN1, DHTTYPE);
DHT dht2(DHTPIN2, DHTTYPE);
DHT dht3(DHTPIN3, DHTTYPE);

void setup() {
  Serial.begin(9600); 
  dht1.begin();
  dht2.begin();
  dht3.begin();
  delay(2000);
}

void loop() {
  float h1 = dht1.readHumidity();
  float t1 = dht1.readTemperature();
  float h2 = dht2.readHumidity();
  float t2 = dht2.readTemperature();
  float h3 = dht3.readHumidity();
  float t3 = dht3.readTemperature();

  if (!isnan(h1) && !isnan(t1) && !isnan(h2) && !isnan(t2) && !isnan(h3) && !isnan(t3)) {
    // Envoi au format JSON pour le script Python
    Serial.print("{");
    Serial.print("\"temp1\":"); Serial.print(t1); Serial.print(",");
    Serial.print("\"hum1\":"); Serial.print(h1); Serial.print(",");
    Serial.print("\"temp2\":"); Serial.print(t2); Serial.print(",");
    Serial.print("\"hum2\":"); Serial.print(h2); Serial.print(",");
    Serial.print("\"temp3\":"); Serial.print(t3); Serial.print(",");
    Serial.print("\"hum3\":"); Serial.print(h3);
    Serial.println("}");
  }
  delay(5000); // Envoi toutes les 5 secondes
}
```

### Branchement Proteus
- **ATmega TX (Pin 1)** -> **COMPIM RXD**
- **ATmega RX (Pin 0)** -> **COMPIM TXD**
- **COMPIM Config** : Port `COM1`, Baud Rate `9600`.

---

## 2. Partie Passerelle (PC Client)

Le script de relais se trouve ici : `backend/thingsboard_relay.py`.
1. Installez **Virtual Serial Port Driver (VSPD)** et créez une paire **COM1 <-> COM2**.
2. Installez les dépendances : `pip install pyserial requests`.
3. Lancez le script : `python backend/thingsboard_relay.py`.

---

## 3. Configuration ThingsBoard (Cloud)

Voici où trouver vos informations sur [demo.thingsboard.io](https://demo.thingsboard.io) :

1. **Access Token** (Déjà configuré : `A5nfCs8VOOzz97F0sD4h`) :
   - Allez dans `Entities` -> `Devices`.
   - Cliquez sur votre appareil.
   - Bouton `Manage Credentials` -> `Access Token`.

2. **Device ID** (Nécessaire pour certaines fonctions avancées) :
   - Cliquez sur votre appareil.
   - Dans l'onglet `Details`, cherchez `ID` (ex: `550e8400-e29b...`).

3. **Dashboard** :
   - Allez dans `Dashboards`.
   - Créez un nouveau Dashboard.
   - Ajoutez un widget "Cards" -> "Attributes Card" ou "Timeseries Chart".
   - Sélectionnez votre appareil comme source de données.

---

## 4. Intégration dans l'App (Next.js)

Le service est prêt dans `frontend/src/services/thingsboard.service.ts`.
Pour l'utiliser dans un composant :

```typescript
import { getLiveTelemetry } from "@/services/thingsboard.service";

// Dans votre composant
const data = await getLiveTelemetry();
console.log("Température réelle :", data.temp1);
```

---

**Tout est prêt !** Vos fichiers sont configurés avec vos identifiants réels. Vous pouvez maintenant lancer Proteus et votre script de relais pour voir les données monter dans le Cloud.
