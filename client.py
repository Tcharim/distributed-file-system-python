import os
from common.utils import send_request
from common.protocol import *
from dotenv import load_dotenv

load_dotenv()
# Adresse du serveur de métadonnées
METADATA_SERVER = tuple(os.getenv("METADATA_SERVER").split(":")) 
METADATA_SERVER = (METADATA_SERVER[0], int(METADATA_SERVER[1]))

# Liste des fichiers disponibles
def list_files():
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_LIST})
    if response["status"] != STATUS_OK:
        print("Error:", response.get("status"))
        return
    print("Files on the system:")
    for file in response.get("files", []):
        print("\t",file)

# Lecture d'un fichier
def read_file(filename):
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_READ, "filename": filename})
    if response["status"] != STATUS_OK:
        print("Error: ", response.get("status"))
        return

    storage_ip, storage_port = response["storage"]
    storage_port = int(storage_port) if isinstance(storage_port, str) else storage_port

    resp2 = send_request(storage_ip, storage_port, {"action": ACTION_READ, "filename": filename})
    if resp2["status"] == STATUS_OK:
        print(resp2["data"])
    else:
        print("Error: ", resp2.get("status"))

# Création d'un fichier
def create_file(filename, data=""):
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_CREATE, "filename": filename})
    if response["status"] != STATUS_OK:
        print("Error:", response.get("status"))
        return

    storage_ip, storage_port = response["storage"]
    storage_port = int(storage_port) if isinstance(storage_port, str) else storage_port

    resp2 = send_request(storage_ip, storage_port, {"action": ACTION_CREATE, "filename": filename, "data": data})
    if resp2["status"] != STATUS_OK:
        print("Error: ", resp2.get("status"))
    else:
        print("File created successfully.")

# Écriture d'un fichier
def write_file(filename, data):
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_LOCK, "filename": filename})
    if response["status"] != STATUS_OK:
        print("Error:", response.get("status"), " File already opened by another client.")
        return

    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_WRITE, "filename": filename, "data": data})
    if response["status"] != STATUS_OK:
        print("Error: ", response.get("status"))
        response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_UNLOCK, "filename": filename})
        return
    
    storage_ip, storage_port = response["storage"]
    storage_port = int(storage_port) if isinstance(storage_port, str) else storage_port

    resp2 = send_request(storage_ip, storage_port, {"action": ACTION_WRITE, "filename": filename, "data": data})
    if resp2["status"] == STATUS_OK:
        print("File written successfully.")
    else:
        print("Error: ", resp2.get("status"))

        
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_UNLOCK, "filename": filename})

# Suppression d'un fichier
def delete_file(filename):
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_LOCK, "filename": filename})
    if response["status"] != STATUS_OK:
        print("Error:", response.get("status"), " File already opened by another client.")
        return
    
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_DELETE, "filename": filename})
    if response["status"] != STATUS_OK:
        print("Error: ", response.get("status"))
        return
    storage_ip, storage_port = response["storage"]
    storage_port = int(storage_port) if isinstance(storage_port, str) else storage_port

    resp2 = send_request(storage_ip, storage_port, {"action": ACTION_DELETE, "filename": filename})
    if resp2["status"] == STATUS_OK:
        print("File deleted successfully.")
    else: 
        print("Error: ", resp2.get("status"))
    
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_UNLOCK, "filename": filename})

if __name__ == "__main__":
    try:
        while True:
            command = input("> ").strip().split()
            if not command:
                continue
            
            action = command[0].lower()
            if action == "list" or action == "ls":
                list_files()
            elif action == "create" and len(command) > 1:
                filename = command[1]
                data = " ".join(command[2:]) if len(command) > 2 else ""
                create_file(filename, data)
            elif action == "read" and len(command) > 1:
                read_file(command[1])
            elif action == "write" and len(command) > 2:
                filename = command[1]
                data = " ".join(command[2:])
                write_file(filename, data)
            elif (action == "delete" or action == "del") and len(command) > 1:
                delete_file(command[1])        
            elif action == "exit":
                print("Goodbye!")
                break
            else:
                print("Usage:\n\t list (alias ls)\n\t create <filename> [data]\n\t read <filename>\n\t write <filename> <data>\n\t delete (alias del) <filename>\n\t exit")
    except KeyboardInterrupt:
        print("Goodbye!")
    except Exception as e:
        print(f"Exiting with error: {e.__class__.__name__}")