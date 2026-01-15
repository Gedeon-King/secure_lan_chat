import sys
import os

# Ajout du dossier src au path pour importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from crypto.crypto_manager import CryptoManager

def test_crypto_flow():
    print("=== DÉBUT DES TESTS CRYPTO ===")

    # 1. Simuler deux utilisateurs : Alice et Bob
    alice = CryptoManager()
    bob = CryptoManager()

    print("[*] Génération des clés éphémères ECDH...")
    alice_pub_pem = alice.generate_ephemeral_keys()
    bob_pub_pem = bob.generate_ephemeral_keys()
    
    print(f"    - Alice PubKey Len: {len(alice_pub_pem)} bytes")
    print(f"    - Bob PubKey Len: {len(bob_pub_pem)} bytes")

    # 2. Échange de clés (Simulé)
    print("\n[*] Calcul du secret partagé et dérivation des clés...")
    alice_fingerprint = alice.compute_shared_secret(bob_pub_pem)
    bob_fingerprint = bob.compute_shared_secret(alice_pub_pem)

    print(f"    - Alice Session Key: {alice.session_key.hex()[:16]}... (masqué)")
    print(f"    - Bob Session Key  : {bob.session_key.hex()[:16]}... (masqué)")
    print(f"    - Alice SAS Fingerprint: {alice_fingerprint}")
    print(f"    - Bob SAS Fingerprint  : {bob_fingerprint}")

    if alice.session_key == bob.session_key:
        print("    [SUCCESS] Les clés de session sont identiques.")
    else:
        print("    [FAIL] CRITIQUE : Les clés de session diffèrent !")
        return

    if alice_fingerprint == bob_fingerprint:
        print("    [SUCCESS] Les fingerprints SAS correspondent.")
    else:
        print("    [FAIL] CRITIQUE : Les fingerprints diffèrent !")
        return

    # 3. Chiffrement / Déchiffrement
    print("\n[*] Test de transport sécurisé (AES-256-GCM)...")
    message_original = "Ceci est un message top secret pour le projet de cybersécurité."
    print(f"    - Message clair : '{message_original}'")

    encrypted_blob = alice.encrypt_message(message_original)
    print(f"    - Message chiffré (Hex) : {encrypted_blob.hex()[:64]}... [Len: {len(encrypted_blob)}]")

    decrypted_msg_bob = bob.decrypt_message(encrypted_blob)
    print(f"    - Message déchiffré par Bob : '{decrypted_msg_bob}'")

    if decrypted_msg_bob == message_original:
        print("    [SUCCESS] Déchiffrement réussi et intégrité vérifiée.")
    else:
        print("    [FAIL] Le message déchiffré ne correspond pas !")

    # 4. Test d'altération (Tampering) - MITM Attack Simulation
    print("\n[*] Simulation d'attaque : Altération du message chiffré (Tampering)...")
    # On corrompt un octet au milieu du ciphertext
    corrupted_blob = bytearray(encrypted_blob)
    corrupted_blob[20] = corrupted_blob[20] ^ 0xFF # Flip bits
    corrupted_blob = bytes(corrupted_blob)

    try:
        bob.decrypt_message(corrupted_blob)
        print("    [FAIL] Bob a accepté un message corrompu sans erreur !")
    except ValueError as e:
        print(f"    [SUCCESS] Bob a rejeté le message corrompu : {e}")

    print("\n=== FIN DES TESTS CRYPTO ===")

if __name__ == "__main__":
    test_crypto_flow()
