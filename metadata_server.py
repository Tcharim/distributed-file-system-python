import os
import socket
import threading
import json
from common.utils import send_request
from common.protocol import *
from dotenv import load_dotenv


# Chargement des variables d'environnement
load_dotenv()
storage_servers = []
for server in os.getenv("STORAGE_SERVERS").split(","):
    ip, port = server.split(":")
    storage_servers.append((ip, int(port)))

files = {}
locks = set()

# Liste des fichiers disponibles dans les serveurs de stockage
def list_storages():
    for (ip, port) in storage_servers:
        try:
            response = send_request(ip, port, {"action": ACTION_LIST})
        except Exception as e:
            print(f"Error connecting to storage server {ip}:{port}: {e.__class__.__name__}")
            continue
        temp_files = response.get("files", [])
        for f in temp_files:
            files[f] = (ip, port)

# Sélection d'un serveur de stockage pour un fichier
def select_storage(filename):
    # Choix simple : hash du nom du fichier
    idx = hash(filename) % len(storage_servers)
    return storage_servers[idx]

# Gestion des requêtes clients
def handle_client(conn, addr):
    data = conn.recv(4096).decode()
    request = json.loads(data)
    print(f"-Received request from {addr}: {request}")
    action = request["action"]
    filename = request.get("filename", "")

    response = {}

    # Traitement de la création de fichiers
    if action == ACTION_CREATE:
        storage = select_storage(filename)
        files[filename] = storage
        response = {"status": STATUS_OK, "storage": storage}

    # Traitement de la lecture, écriture et suppression de fichiers
    elif action == ACTION_READ or action == ACTION_WRITE or action == ACTION_DELETE:
        if filename not in files:
            response = {"status": STATUS_ERROR_FILE_NOT_FOUND}
        else:
            storage = files[filename]
            response = {"status": STATUS_OK, "storage": storage}
            if action == ACTION_DELETE:
                del files[filename]

    # Traitement du verrouillage de fichiers
    elif action == ACTION_LOCK:
        if filename in locks:
            response = {"status": STATUS_ERROR_FILE_LOCKED}
        else:
            locks.add(filename)
            response = {"status": STATUS_OK}

    # Traitement du déverrouillage de fichiers
    elif action == ACTION_UNLOCK:
        locks.discard(filename)
        response = {"status": STATUS_OK}

    # Traitement de la liste des fichiers
    elif action == ACTION_LIST:
        response = {"status": STATUS_OK, "files": list(files.keys())}

    else:
        response = {"status": STATUS_ERROR_UNKNOWN}

    print(f"-Sending response to {addr}: {response}")

    conn.send(json.dumps(response).encode())
    conn.close()


def main():
    METADATA_SERVER = tuple(os.getenv("METADATA_SERVER").split(":"))
    METADATA_SERVER = (METADATA_SERVER[0], int(METADATA_SERVER[1]))

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(METADATA_SERVER)
    server.listen(5)

    server.settimeout(1)

    print(f"Metadata server running on port {METADATA_SERVER[1]}")

    list_storages()

    try:
        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(
                    target=handle_client,
                    args=(conn, addr),
                    daemon=True
                ).start()

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("\nStopping Metadata server")

    finally:
        server.close()
        print("Metadata server stopped cleanly.")

if __name__ == "__main__":
    main()
