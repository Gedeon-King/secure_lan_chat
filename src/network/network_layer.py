import socket
import threading
import struct
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [NETWORK] - %(message)s')

class NetworkManager:
    """
    Gère la communication réseau fiable sur TCP.
    - Supporte mode Serveur (Attente de connexion) et Client (Connexion sortante).
    - Utilise un préfixe de longueur (4 bytes Big Endian) pour le framing des messages,
      évitant les problèmes de collage/découpage de paquets TCP.
    """

    def __init__(self, on_receive_callback=None, on_disconnect_callback=None):
        self.sock = None        # Socket principal
        self.conn = None        # Socket de connexion active (pour envoyer/recevoir)
        self.address = None     # Adresse du pair
        self.is_server = False
        self.running = False
        self.on_receive = on_receive_callback
        self.on_disconnect = on_disconnect_callback
        self.receive_thread = None

    def start_server(self, port, host='0.0.0.0'):
        """Démarre le socket serveur et attend UNE connexion."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permet de redémarrer rapidement
            self.sock.bind((host, port))
            self.sock.listen(1)
            self.is_server = True
            logging.info(f"Serveur en écoute sur {host}:{port}")
            
            # Bloquant jusqu'à connexion (pour simplifier le flux)
            self.conn, self.address = self.sock.accept()
            logging.info(f"Connexion entrante acceptée de {self.address}")
            
            self.running = True
            self._start_receive_thread()
            return True
        except Exception as e:
            logging.error(f"Erreur démarrage serveur: {e}")
            return False

    def connect_to_peer(self, ip, port):
        """Connecte ce client à un pair distant."""
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((ip, port))
            self.address = (ip, port)
            self.is_server = False
            logging.info(f"Connecté avec succès à {ip}:{port}")
            
            self.running = True
            self._start_receive_thread()
            return True
        except Exception as e:
            logging.error(f"Erreur connexion vers {ip}:{port} : {e}")
            return False

    def send_bytes(self, data: bytes):
        """Envoie des données brutes avec un header de longueur."""
        if not self.conn or not self.running:
            logging.error("Tentative d'envoi sans connexion active.")
            return False

        try:
            # Framing: [Length (4B)][Data]
            header = struct.pack('!I', len(data))
            self.conn.sendall(header + data)
            return True
        except Exception as e:
            logging.error(f"Erreur d'envoi: {e}")
            self.close()
            return False

    def _start_receive_thread(self):
        """Lance le thread de réception."""
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()

    def _receive_loop(self):
        """Boucle de réception qui gère le découpage des messages."""
        buffer = b""
        payload_size = None

        logging.info("Démarrage de la boucle de réception.")
        
        while self.running and self.conn:
            try:
                # On lit par chunks
                data = self.conn.recv(4096)
                if not data:
                    logging.info("Connexion fermée par le pair (EOF).")
                    break
                
                buffer += data

                # Traitement du buffer pour extraire les messages complets
                while True:
                    # 1. Lire la taille si on ne l'a pas encore
                    if payload_size is None:
                        if len(buffer) >= 4:
                            payload_size = struct.unpack('!I', buffer[:4])[0]
                            buffer = buffer[4:] # Retirer le header
                        else:
                            break # Pas assez de données pour le header

                    # 2. Lire le payload si on a la taille
                    if payload_size is not None:
                        if len(buffer) >= payload_size:
                            payload = buffer[:payload_size]
                            buffer = buffer[payload_size:] # Retirer le payload
                            
                            # Reset pour le prochain message
                            payload_size = None
                            
                            # Callback
                            if self.on_receive:
                                try:
                                    self.on_receive(payload)
                                except Exception as e:
                                    logging.error(f"Erreur dans le callback on_receive: {e}")
                        else:
                            break # Pas assez de données pour le payload complet

            except Exception as e:
                logging.error(f"Erreur réception: {e}")
                break
        
        # Nettoyage final
        self.close()

    def close(self):
        """Ferme la connexion proprement."""
        self.running = False
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
            
        logging.info("Connexion réseau fermée.")
        if self.on_disconnect:
            self.on_disconnect()
