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



def listen_to_server(sock, game_state_callback):
    buffer = ""
    while True:
        data = sock.recv(1024).decode()
        buffer += data
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            msg = json.loads(line)
            if msg["type"] == "game_state":
                game_state_callback(msg["data"])