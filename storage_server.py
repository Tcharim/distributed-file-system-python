import socket
import threading
import os
import json
from common.protocol import *

STORAGE_DIR = "data_"  # Chaque serveur a son propre dossier

def handle_client(conn, addr, server_dir):
    data = conn.recv(4096).decode()
    request = json.loads(data)
    print(f"-Received request from {addr}: {request}")
    action = request["action"]
    filename = request.get("filename", "")
    content = request.get("data", "")

    filepath = os.path.join(server_dir, filename)
    response = {}

    if action == ACTION_READ:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                response = {"status": STATUS_OK, "data": f.read()}
        else:
            response = {"status": STATUS_ERROR_FILE_NOT_FOUND}

    elif action == ACTION_CREATE:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        response = {"status": STATUS_OK}

    elif action == ACTION_WRITE:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)
        response = {"status": STATUS_OK}

    elif action == ACTION_DELETE:
        if os.path.exists(filepath):
            os.remove(filepath)
            response = {"status": STATUS_OK}
        else:
            response = {"status": STATUS_ERROR_FILE_NOT_FOUND}
    elif action == ACTION_LIST:
        files = os.listdir(server_dir)
        response = {"status": STATUS_OK, "files": files}
    else:
        response = {"status": STATUS_ERROR_UNKNOWN}

    print(f"-Sending response to {addr}: {response}")
    conn.send(json.dumps(response).encode())
    conn.close()

def main(port, server_dir):
    os.makedirs(server_dir, exist_ok=True)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", port))
    
    server.listen(5)
    
    server.settimeout(1)

    print(f"Storage server listening on port {port}")

    try:
        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(
                    target=handle_client,
                    args=(conn, addr, server_dir),
                    daemon=True
                ).start()

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("\nStopping storage server")

    finally:
        server.close()
        print("Storage server stopped cleanly.")

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1])

    server_dir = STORAGE_DIR + str(port)
    main(port, server_dir)
