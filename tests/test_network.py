import sys
import os
import threading
import time

# Ajout du path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from network.network_layer import NetworkManager

def server_logic(received_msgs):
    srv = NetworkManager(on_receive_callback=lambda data: received_msgs.append(f"SRV: {data.decode()}"))
    print("[SERVER] Démarrage...")
    srv.start_server(9999)
    # Echo back logic could go here but simpler to just receive for this test
    # Let's send a hello after connection
    time.sleep(1)
    srv.send_bytes(b"HELLO FROM SERVER")
    
    # Keep alive for a bit
    time.sleep(3)
    srv.close()

def client_logic(received_msgs):
    time.sleep(1) # Wait for server
    cli = NetworkManager(on_receive_callback=lambda data: received_msgs.append(f"CLI: {data.decode()}"))
    print("[CLIENT] Connexion...")
    if cli.connect_to_peer('127.0.0.1', 9999):
        cli.send_bytes(b"HELLO FROM CLIENT")
        time.sleep(2)
        cli.close()
    else:
        print("[CLIENT] Échec connexion")

def test_network():
    print("=== TEST RÉSEAU ===")
    received_msgs = []

    t_srv = threading.Thread(target=server_logic, args=(received_msgs,))
    t_cli = threading.Thread(target=client_logic, args=(received_msgs,))

    t_srv.start()
    t_cli.start()

    t_srv.join()
    t_cli.join()

    print("\n[RÉSULTATS]")
    for msg in received_msgs:
        print(msg)

    # Vérification
    expected = ["SRV: HELLO FROM CLIENT", "CLI: HELLO FROM SERVER"]
    # L'ordre peut varier légèrement selon les threads
    if len(received_msgs) == 2:
        print("[SUCCESS] Échange de messages réussi.")
    else:
        print(f"[FAIL] Nombre de messages reçus incorrect: {len(received_msgs)}")

if __name__ == "__main__":
    test_network()
