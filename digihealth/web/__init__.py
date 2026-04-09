import os 
from flask import Flask, render_template, jsonify, request
from ..config import config
from ..logger import logger
import logging

# Silenzia i log tecnici di Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Il resto del codice che abbiamo scritto prima...
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')

# Inizializza Flask specificando esplicitamente dove sono i template
app = Flask(__name__, template_folder=template_dir)


# Stato globale che verrà consumato dall'HTML tramite le chiamate /status
state = {
    "active": False,
    "mode": "IDLE",
    "countdown": 0,
    "level": 0,
    "th_tol": 40,
    "th_crit": 70,
    "volume": 0.5,
    "spectrum": [0] * 20,
    "air_quality": {
        "temp": "--",
        "humidity": "--",
        "co2": "--",
        "iaqi": "--"
    }
}

@app.route('/')
def index():
    # Flask cercherà automaticamente in templates/dashboard.html
    return render_template('dashboard.html')

@app.route('/status')
def get_status():
    return jsonify(state)

@app.route('/toggle')
def toggle():
    state["active"] = not state["active"]
    state["mode"] = "CHECK" if state["active"] else "IDLE"
    logger.info(f"Switch Web: {'ON' if state['active'] else 'OFF'}")
    return jsonify({"status": "ok", "active": state["active"]})

# ... mantieni gli altri endpoint (/calibrate, /set_volume) come prima ...

class WebManager:
    def __init__(self):
        self.host = config.web.host
        self.port = config.web.port

    def update_data(self, processed_data):
        """Riceve i dati dal main.py e aggiorna il dizionario 'state'"""
        try:
            state["level"] = processed_data.get('audio_level', 0)
            state["air_quality"]["iaqi"] = processed_data.get('IAQI', '--')
            state["air_quality"]["temp"] = processed_data.get('temperature', '--')
            # Eccetera...
        except Exception as e:
            logger.error(f"Errore update web: {e}")

    def run(self):
        app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
