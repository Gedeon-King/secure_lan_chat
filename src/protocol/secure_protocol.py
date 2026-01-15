import logging
import threading
from enum import Enum

# Imports des couches inférieures
from network.network_layer import NetworkManager
from crypto.crypto_manager import CryptoManager

class ProtocolState(Enum):
    IDLE = 0
    HANDSHAKING = 1
    SECURE = 2

class SecureMessenger:
    """
    Orchestrateur de la sécurité.
    Gère le cycle de vie : Connection -> Handshake (ECDH) -> Secure Transport.
    """
    
    # Types de paquets (1 byte prefix)
    TYPE_HANDSHAKE = b'\x01'
    TYPE_MESSAGE   = b'\x02'

    def __init__(self, on_message_received, on_status_change):
        self.net = NetworkManager(
            on_receive_callback=self._handle_network_data,
            on_disconnect_callback=self._on_disconnect
        )
        self.crypto = CryptoManager()
        self.state = ProtocolState.IDLE
        
        # Callbacks vers l'UI
        self.on_message_received = on_message_received
        self.on_status_change = on_status_change # (status_msg, is_secure, fingerprint)

    def start_server(self, port):
        """Démarre en mode serveur (attente)."""
        self._set_status("En attente de connexion...", False)
        if self.net.start_server(port):
            self._start_handshake()
        else:
            self._set_status("Erreur démarrage serveur", False)

    def connect(self, ip, port):
        """Démarre en mode client (connexion)."""
        self._set_status(f"Connexion vers {ip}:{port}...", False)
        if self.net.connect_to_peer(ip, port):
            self._start_handshake()
        else:
            self._set_status("Erreur de connexion", False)

    def send_message(self, text):
        """Envoie un message texte (uniquement si sécurisé)."""
        if self.state != ProtocolState.SECURE:
            logging.warning("Tentative d'envoi hors session sécurisée.")
            return False
        
        try:
            encrypted_blob = self.crypto.encrypt_message(text)
            # Packet: [TYPE_MESSAGE][EncryptedBlob]
            self.net.send_bytes(self.TYPE_MESSAGE + encrypted_blob)
            return True
        except Exception as e:
            logging.error(f"Erreur chiffrement/envoi: {e}")
            return False

    def close(self):
        self.net.close()
        self.state = ProtocolState.IDLE

    # --- Interne ---

    def _set_status(self, msg, is_secure, fingerprint=None):
        if self.on_status_change:
            self.on_status_change(msg, is_secure, fingerprint)

    def _start_handshake(self):
        """Initie le handshake : génère clés et envoie la PubKey."""
        self.state = ProtocolState.HANDSHAKING
        self._set_status("Génération des clés ECDH...", False)
        
        try:
            my_pub_pem = self.crypto.generate_ephemeral_keys()
            # Packet: [TYPE_HANDSHAKE][PEM]
            self.net.send_bytes(self.TYPE_HANDSHAKE + my_pub_pem)
            self._set_status("Clé publique envoyée. Attente du pair...", False)
        except Exception as e:
            logging.error(f"Erreur handshake init: {e}")
            self.close()

    def _handle_network_data(self, data):
        """Switch sur le type de paquet."""
        if len(data) < 1:
            return

        msg_type = data[0:1]
        payload = data[1:]

        if msg_type == self.TYPE_HANDSHAKE:
            self._handle_handshake_packet(payload)
        elif msg_type == self.TYPE_MESSAGE:
            self._handle_secure_message_packet(payload)
        else:
            logging.warning(f"Type de paquet inconnu reçu: {msg_type}")

    def _handle_handshake_packet(self, peer_pub_key_pem):
        """Reçoit la clé du pair, calcule le secret."""
        if self.state not in [ProtocolState.HANDSHAKING, ProtocolState.IDLE]:
            # Re-keying non supporté pour l'instant
            return

        try:
            fingerprint = self.crypto.compute_shared_secret(peer_pub_key_pem)
            self.state = ProtocolState.SECURE
            self._set_status("CANAL SÉCURISÉ ÉTABLI", True, fingerprint)
            logging.info(f"Handshake terminé. SAS Fingerprint: {fingerprint}")
        except Exception as e:
            logging.error(f"Erreur handshake finish: {e}")
            self._set_status("Erreur critique Handshake", False)
            self.close()

    def _handle_secure_message_packet(self, encrypted_blob):
        """Déchiffre et notifie l'UI."""
        if self.state != ProtocolState.SECURE:
            logging.warning("Message chiffré reçu avant fin handshake.")
            return

        try:
            plaintext = self.crypto.decrypt_message(encrypted_blob)
            if self.on_message_received:
                self.on_message_received(plaintext)
        except ValueError as e:
            logging.error(f"Intégrité violée ! Message rejeté : {e}")
            # Optionnel: Fermer la connexion en cas d'attaque
        except Exception as e:
            logging.error(f"Erreur déchiffrement: {e}")

    def _on_disconnect(self):
        self.state = ProtocolState.IDLE
        self._set_status("Déconnecté", False)
