import sys
import os
import threading
import time

# Ajout du path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from protocol.secure_protocol import SecureMessenger

def server_logic(events):
    def on_msg(text):
        events.append(f"SRV_RECV: {text}")
    
    def on_status(msg, secure, fp):
        print(f"[SERVER STATUS] {msg} (Secure: {secure}, FP: {fp})")
        if secure:
            events.append(f"SRV_SECURE_FP: {fp}")

    messenger = SecureMessenger(on_msg, on_status)
    print("[SERVER] Start...")
    messenger.start_server(8888)
    
    # Wait for secure state
    time.sleep(2) 
    
    messenger.send_message("Bienvenue dans le chat sécurisé Alice.")
    time.sleep(3)
    messenger.close()

def client_logic(events):
    def on_msg(text):
        events.append(f"CLI_RECV: {text}")

    def on_status(msg, secure, fp):
        print(f"[CLIENT STATUS] {msg} (Secure: {secure}, FP: {fp})")
        if secure:
            events.append(f"CLI_SECURE_FP: {fp}")

    time.sleep(1) # Wait for server
    messenger = SecureMessenger(on_msg, on_status)
    print("[CLIENT] Connect...")
    messenger.connect('127.0.0.1', 8888)
    
    time.sleep(1) # Wait for secure
    messenger.send_message("Merci Bob. La crypto est active ?")
    
    time.sleep(3)
    messenger.close()

def test_protocol():
    print("=== TEST PROTOCOLE SÉCURISÉ ===")
    events = []

    t_srv = threading.Thread(target=server_logic, args=(events,))
    t_cli = threading.Thread(target=client_logic, args=(events,))

    t_srv.start()
    t_cli.start()

    t_srv.join()
    t_cli.join()

    print("\n[RÉSULTATS]")
    for e in events:
        print(e)
    
    # Validation
    # On doit trouver les Fingerprints (identiques)
    fps = [e.split(': ')[1] for e in events if 'FP' in e]
    if len(fps) >= 2 and fps[0] == fps[1]:
         print("[SUCCESS] Handshake terminé et Fingerprints identiques.")
    else:
         print(f"[FAIL] Fingerprints incohérents ou manquants : {fps}")

    # On doit trouver les messages
    msgs = [e for e in events if 'RECV' in e]
    expected_snippets = ["Bienvenue", "Merci Bob"]
    if len(msgs) == 2 and any("Bienvenue" in m for m in msgs) and any("Merci Bob" in m for m in msgs):
        print("[SUCCESS] Messages chiffrés échangés et déchiffrés.")
    else:
        print("[FAIL] Échange de messages incomplet.")

if __name__ == "__main__":
    test_protocol()
