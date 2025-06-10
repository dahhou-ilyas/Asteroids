import socket
import json
import threading


def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 8080))
    print("Connecté au serveur")

    # Lire le message de bienvenue
    buffer = ""
    while True:
        data = s.recv(1024).decode()
        buffer += data
        if "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            msg = json.loads(line)
            if msg["type"] == "welcome":
                print("ID attribué:", msg["data"]["player_id"])
                return s, msg["data"]["player_id"]

def send_inputs(sock, player_id, inputs):
    msg = {
        "type": "input",
        "data": {
            "player_id": player_id,
            "inputs": inputs
        }
    }
    sock.sendall((json.dumps(msg) + "\n").encode())



def listen_to_server(sock, on_game_state):
    buffer = ""
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                print("Déconnecté du serveur.")
                break
            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                
                msg = json.loads(line)
                
                if msg["type"] == "game_state":
                    on_game_state(msg["data"])

        except Exception as e:
            print(f"Erreur réseau : {e}")
            break



def send_message(sock, message):
    # Convertir en JSON + ajout de "\n" comme séparateur
    data = json.dumps(message) + "\n"
    sock.sendall(data.encode())

