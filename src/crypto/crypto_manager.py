import os
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidTag

class CryptoManager:
    """
    Gère toutes les opérations cryptographiques :
    - Génération de paires de clés (ECDH)
    - Échange de clés et calcul du secret partagé
    - Dérivation de clés (HKDF)
    - Chiffrement et Déchiffrement Authentifié (AES-GCM)
    """

    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.shared_secret = None
        self.session_key = None
        self.fingerprint = None

    def generate_ephemeral_keys(self):
        """
        Génère une paire de clés éphémère (ECDH sur SECP384R1).
        Retourne la clé publique sérialisée (PEM) pour l'envoi au pair.
        """
        self.private_key = ec.generate_private_key(ec.SECP384R1())
        self.public_key = self.private_key.public_key()
        
        pem_public = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem_public

    def compute_shared_secret(self, peer_public_key_pem):
        """
        Calcule le secret partagé à partir de la clé publique du pair.
        Dérive ensuite la clé de session et le fingerprint.
        """
        if not self.private_key:
            raise ValueError("Clés locales non générées.")

        peer_public_key = serialization.load_pem_public_key(peer_public_key_pem)
        
        # ECDH Exchange
        self.shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)

        # Key Derivation (HKDF)
        # On dérive 32 bytes pour AES-256
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None, # Dans un cas réel, échanger un sel aléatoire est mieux, mais ECDH garantit déjà une haute entropie
            info=b'secure-lan-chat-v1-session'
        )
        self.session_key = hkdf.derive(self.shared_secret)

        # Génération d'un Fingerprint visuel pour authentification SAS (Short Authentication String)
        # On hash la clé de session pour avoir une chaine vérifiable
        fingerprint_hash = hashlib.sha256(self.session_key).hexdigest()
        # On prend les 8 premiers caractères et on les groupe pour la lisibilité
        self.fingerprint = f"{fingerprint_hash[:4].upper()} {fingerprint_hash[4:8].upper()}"

        return self.fingerprint

    def encrypt_message(self, plaintext_str):
        """
        Chiffre un message texte avec AES-256-GCM.
        Format sortie : [Nonce 12b][Ciphertext + Tag]
        """
        if not self.session_key:
            raise ValueError("Session non établie. Pas de clé de session.")

        # AES-GCM nécessite un nonce unique par message.
        aesgcm = AESGCM(self.session_key)
        nonce = os.urandom(12)
        
        data = plaintext_str.encode('utf-8')
        # encrypt retourne ciphertext + tag appele "ciphertext" dans la doc AESGCM
        ciphertext_blob = aesgcm.encrypt(nonce, data, None)
        
        return nonce + ciphertext_blob

    def decrypt_message(self, encrypted_blob):
        """
        Déchiffre un blob binaire. Vérifie l'intégrité (Tag).
        """
        if not self.session_key:
            raise ValueError("Session non établie.")

        if len(encrypted_blob) < 12:
             raise ValueError("Message invalide (trop court).")

        nonce = encrypted_blob[:12]
        ciphertext_with_tag = encrypted_blob[12:]
        
        aesgcm = AESGCM(self.session_key)
        
        try:
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
            return plaintext_bytes.decode('utf-8')
        except InvalidTag:
            raise ValueError("Échec de l'intégrité du message ! Modification détectée ou clé incorrecte.")

