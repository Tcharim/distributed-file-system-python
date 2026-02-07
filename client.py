from common.utils import send_request
from common.protocol import *

# TODO: ajouter des fonctions pour supprimer des fichiers, lister les fichiers, etc.
METADATA_SERVER = ("127.0.0.1", 8000)

def list_files():
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_LIST})
    if response["status"] != STATUS_OK:
        print("Error:", response.get("status"))
        return
    print("Files on the system:")
    for file in response.get("files", []):
        print("\t",file)

def create_file(filename, data=""):
    # Demande au serveur de métadonnées où stocker le fichier
    response = send_request(METADATA_SERVER[0], METADATA_SERVER[1], {"action": ACTION_CREATE, "filename": filename})
    if response["status"] != STATUS_OK:
        print("Error:", response.get("status"))
        return

    storage_ip, storage_port = response["storage"]
    storage_port = int(storage_port) if isinstance(storage_port, str) else storage_port

    # Écrire le fichier sur le serveur de stockage
    resp2 = send_request(storage_ip, storage_port, {"action": ACTION_CREATE, "filename": filename, "data": data})
    if resp2["status"] != STATUS_OK:
        print("Error: ", resp2.get("status"))
    else:
        print("File created successfully.")


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
                break
            else:
                print("Usage:\n\t list alias ls\n\t create <filename> [data]\n\t read <filename>\n\t write <filename> <data>\n\t delete (alias del) <filename>\n\t exit")
    except KeyboardInterrupt:
        print("\nInterrupted, exiting...")