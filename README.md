# DigiHealth Lamp

Una lampada smart basata su Raspberry Pi per il monitoraggio ambientale e l'invio dati a InfluxDB tramite Telegraf.

## Caratteristiche

- **Sensori Ambientali**: ZPH01B (PM2.5, CO2, TVOC, temperatura, umidità), BH1750 (luminosità)
- **Sensori opzionali**: porta, finestra, conteggio persone via telecamera RTSP (disabilitati di default)
- **Calcolo IAQI**: Indice di Qualità dell'Aria Interna
- **Attuatori**: NeoPixel LED RGB, Shelly Smart Lamp, Faretti LED WiFi dimmerabili (circadiani)
- **Dashboard Web**: Monitoraggio in tempo reale (opzionale)
- **Comunicazione**: InfluxDB via Telegraf
- **Modulare**: Estensioni opzionali caricabili dinamicamente

## Installazione su Raspberry Pi

### Prerequisiti

- Raspberry Pi (consigliato 4 o superiore)
- Raspbian OS
- Python 3.7+
- Connessioni hardware:
  - ZPH01B collegato a `/dev/serial0` (UART)
  - BH1750 collegato a I2C bus 1, indirizzo 0x23
  - NeoPixel collegati a GPIO 12
  - Shelly lamp accessibile via HTTP

### Passi di Installazione

1. **Clona il repository**:
   ```bash
   git clone https://github.com/yourusername/digihealth-lamp.git
   cd digihealth-lamp
   ```

2. **Installa le dipendenze di sistema**:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-dev
   ```

3. **Abilita interfacce hardware**:
   ```bash
   sudo raspi-config
   # Interfacing Options > I2C > Enable
   # Interfacing Options > Serial > Enable, disable console
   ```

4. **Installa il package**:
   ```bash
   sudo pip3 install -e .
   ```

5. **Configura l'installazione**:
   ```bash
   digihealth-setup
   ```
   Questo comando crea `config/local.yaml` con le impostazioni specifiche per la tua installazione (tag InfluxDB, sensori opzionali, ecc.).

6. **Installa il servizio systemd**:
   ```bash
   sudo cp systemd/digihealth-lamp.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable digihealth-lamp
   sudo systemctl start digihealth-lamp
   ```

7. **Verifica**:
   ```bash
   sudo systemctl status digihealth-lamp
   sudo journalctl -u digihealth-lamp -f
   ```

## Utilizzo

### Avvio Manuale
```bash
digihealth-lamp
```

### Dashboard Web (se abilitata)
Apri http://raspberry-pi-ip:5000 nel browser.

## Configurazione

Il sistema supporta **configurazioni gerarchiche** per adattarsi a installazioni diverse:

### 📁 File di configurazione

1. **`config/default.yaml`** - Configurazione di base (non modificare)
2. **`config/local.yaml`** - Configurazione specifica dell'installazione (creato automaticamente)

### 🏷️ Configurazione tag InfluxDB

I tag InfluxDB possono essere configurati in diversi modi (priorità decrescente):

1. **Variabili d'ambiente** (più sicure per deployment automatizzati):
   ```bash
   export DIGIHEALTH_SENSOR="ZPHS01B"
   export DIGIHEALTH_HOST="raspberry01"
   export DIGIHEALTH_LAMPADA="88a29e6f9779"
   export DIGIHEALTH_STANZA="Ufficio1_ProtoDesign"
   export DIGIHEALTH_CLIENT_ID="57"
   ```

2. **Script di setup interattivo**:
   ```bash
   digihealth-setup
   ```

3. **File `config/local.yaml`** (modifica manuale):
   ```yaml
   communicator:
     telegraf:
       tags:
         sensor: "ZPHS01B"
         host: "raspberry01"
         lampada: "88a29e6f9779"
         stanza: "Ufficio1_ProtoDesign"
         client_id: "57"
   ```

### 🔧 Configurazione sensori/attuatori opzionali

Usa `digihealth-setup` per abilitare:
- **Conteggio persone**: telecamera RTSP con YOLOv8
- **Faretti LED WiFi**: luce circardiana basata su lux
- **Sensori porta/finestra**: GPIO contact sensors

Esempio configurazione completa in `config/local.yaml`:
```yaml
sensors:
  people_counter:
    enabled: true
    rtsp_url: "rtsp://admin:password@192.168.1.124/profile2/media.smp"

actuators:
  led_wifi:
    enabled: true
    ip: "192.168.1.192"
    mode: "circadian"

communicator:
  telegraf:
    tags:
      sensor: "ZPHS01B"
      host: "raspberry01"
      lampada: "88a29e6f9779"
      stanza: "Ufficio1_ProtoDesign"
      client_id: "57"
```

### 🔄 Ordine di caricamento configurazione

1. Carica `config/default.yaml`
2. Sovrascrive con `config/local.yaml` (se esiste)
3. Sovrascrive con variabili d'ambiente (se definite)

Questo permette di avere valori di default sicuri nel repository mentre ogni installazione può personalizzare i propri tag e impostazioni.

## Sviluppo

### Struttura del Progetto
```
digihealth_lamp/
├── digihealth/
│   ├── main.py              # Entry point
│   ├── config.py            # Configurazione
│   ├── logger.py            # Logging
│   ├── sensors/             # Modulo sensori
│   ├── processors/          # Modulo processori
│   ├── actuators/           # Modulo attuatori
│   ├── communicator/        # Modulo comunicazione
│   └── web/                 # Modulo web (opzionale)
├── config/
│   ├── default.yaml         # Configurazione di default
│   └── local.yaml           # Configurazione locale (creato da setup)
├── systemd/
│   └── digihealth-lamp.service
├── docker/
│   └── Dockerfile
├── setup_config.py          # Script di configurazione interattiva
├── requirements.txt
├── setup.py
└── README.md
```

### Aggiungere un Nuovo Sensore

1. Crea una classe che eredita da `BaseSensor` in `sensors/`
2. Aggiungi la configurazione in `config/default.yaml`
3. Registra il sensore in `SensorManager`

### Test

```bash
pip install pytest
pytest tests/
```

## Troubleshooting

- **Errore seriale**: Verifica che UART sia abilitato e non usato dalla console
- **Errore I2C**: Controlla indirizzi con `i2cdetect -y 1`
- **LED non funzionano**: Verifica connessione GPIO 12
- **Shelly non risponde**: Controlla indirizzo IP e connessione di rete

## Licenza

MIT License