#!/usr/bin/env python3
"""
Application Flask pour le chat sécurisé.
Interface web conviviale avec mise à jour en temps réel via SSE (Server-Sent Events).
"""
import sys
import os
import threading
import time
from flask import Flask, render_template, request, jsonify, Response
import logging
import queue

# Ajouter le path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from protocol.secure_protocol import SecureMessenger

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# File de messages pour SSE
message_queue = queue.Queue()

# État de l'application
class AppState:
    def __init__(self):
        self.messenger = None
        self.messages = []
        self.status = "Non connecté"
        self.is_secure = False
        self.fingerprint = None
        self.mode = None  # 'server' ou 'client'
        self.lock = threading.Lock()

state = AppState()

# --- Callbacks du protocole ---

def on_message_received(plaintext):
    """Appelé quand un message est reçu du pair."""
    with state.lock:
        msg_obj = {"from": "Pair", "text": plaintext, "time": time.strftime("%H:%M:%S")}
        state.messages.append(msg_obj)
        # Notification SSE
        message_queue.put({"type": "message", "data": msg_obj})

def on_status_change(status_msg, is_secure, fingerprint=None):
    """Appelé quand le statut change."""
    with state.lock:
        state.status = status_msg
        state.is_secure = is_secure
        state.fingerprint = fingerprint
        # Notification SSE
        message_queue.put({
            "type": "status",
            "data": {
                "status": status_msg,
                "is_secure": is_secure,
                "fingerprint": fingerprint
            }
        })

# --- Routes Flask ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_server', methods=['POST'])
def start_server():
    """Démarre en mode serveur."""
    port = int(request.json.get('port', 9999))
    
    with state.lock:
        if state.messenger:
            return jsonify({"success": False, "error": "Déjà connecté"})
        
        state.messenger = SecureMessenger(on_message_received, on_status_change)
        state.mode = 'server'
        state.messages = []
    
    # Démarrage dans un thread car c'est bloquant
    def run():
        state.messenger.start_server(port)
    
    threading.Thread(target=run, daemon=True).start()
    return jsonify({"success": True})

@app.route('/api/connect', methods=['POST'])
def connect():
    """Connecte à un pair."""
    ip = request.json.get('ip')
    port = int(request.json.get('port', 9999))
    
    with state.lock:
        if state.messenger:
            return jsonify({"success": False, "error": "Déjà connecté"})
        
        state.messenger = SecureMessenger(on_message_received, on_status_change)
        state.mode = 'client'
        state.messages = []
    
    def run():
        state.messenger.connect(ip, port)
    
    threading.Thread(target=run, daemon=True).start()
    return jsonify({"success": True})

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """Envoie un message."""
    text = request.json.get('text', '').strip()
    
    if not text:
        return jsonify({"success": False, "error": "Message vide"})
    
    with state.lock:
        if not state.messenger or not state.is_secure:
            return jsonify({"success": False, "error": "Pas de session sécurisée"})
        
        if state.messenger.send_message(text):
            # Ajouter à notre historique
            msg_obj = {"from": "Moi", "text": text, "time": time.strftime("%H:%M:%S")}
            state.messages.append(msg_obj)
            message_queue.put({"type": "message", "data": msg_obj})
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Erreur d'envoi"})

@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """Ferme la connexion."""
    with state.lock:
        if state.messenger:
            state.messenger.close()
            state.messenger = None
        state.is_secure = False
        state.fingerprint = None
        state.status = "Déconnecté"
        state.mode = None
    return jsonify({"success": True})

@app.route('/api/state')
def get_state():
    """Retourne l'état actuel."""
    with state.lock:
        return jsonify({
            "status": state.status,
            "is_secure": state.is_secure,
            "fingerprint": state.fingerprint,
            "messages": state.messages,
            "mode": state.mode
        })

@app.route('/stream')
def stream():
    """SSE stream pour les mises à jour en temps réel."""
    def event_stream():
        while True:
            try:
                # Timeout pour éviter le blocage
                msg = message_queue.get(timeout=30)
                yield f"data: {jsonify(msg).get_data(as_text=True)}\n\n"
            except queue.Empty:
                # Keepalive
                yield ": keepalive\n\n"
    
    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("=" * 60)
    print("🔐 SECURE LAN CHAT - Interface Web")
    print("=" * 60)
    print("Ouvrez votre navigateur à: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
