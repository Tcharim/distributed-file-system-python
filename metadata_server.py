import os
import socket
import threading
import json
from common.utils import send_request
from common.protocol import *
from dotenv import load_dotenv

load_dotenv()

# Mapping : filename -> storage_server (ip, port)
files = {}
# Verrous des fichiers
locks = set()

# Liste des serveurs de stockage disponibles
storage_servers = [
    tuple(server.split(":")) 
    for server in os.getenv("STORAGE_SERVERS").split(",")
]
storage_servers = [("127.0.0.1", 9001), ("127.0.0.1", 9002)]
PORT = 8000

def list_storages():
    for (ip, port) in storage_servers:
        response = send_request(ip, port, {"action": ACTION_LIST})
        if response["status"] != STATUS_OK:
            print("Error:", response.get("status"))
            return
        temp_files = response.get("files", [])
        for f in temp_files:
            files[f] = (ip, port)

def select_storage(filename):
    # Choix simple : hash du nom du fichier
    idx = hash(filename) % len(storage_servers)
    return storage_servers[idx]

def handle_client(conn, addr):
    data = conn.recv(4096).decode()
    request = json.loads(data)
    print(f"-Received request from {addr}: {request}")
    action = request["action"]
    filename = request.get("filename", "")

    response = {}

    if action == ACTION_CREATE:
        storage = select_storage(filename)
        files[filename] = storage
        response = {"status": STATUS_OK, "storage": storage}

    elif action == ACTION_READ or action == ACTION_WRITE or action == ACTION_DELETE:
        if filename not in files:
            response = {"status": STATUS_ERROR_FILE_NOT_FOUND}
        else:
            storage = files[filename]
            response = {"status": STATUS_OK, "storage": storage}
            if action == ACTION_DELETE:
                del files[filename]

    elif action == ACTION_LOCK:
        if filename in locks:
            response = {"status": STATUS_ERROR_FILE_LOCKED}
        else:
            locks.add(filename)
            response = {"status": STATUS_OK}

    elif action == ACTION_UNLOCK:
        locks.discard(filename)
        response = {"status": STATUS_OK}

    
    elif action == ACTION_LIST:
        response = {"status": STATUS_OK, "files": list(files.keys())}

    else:
        response = {"status": STATUS_ERROR_UNKNOWN}

    print(f"-Sending response to {addr}: {response}")

    conn.send(json.dumps(response).encode())
    conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", PORT))
    server.listen(5)

    server.settimeout(1)

    print(f"Metadata server running on port {PORT}")

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
