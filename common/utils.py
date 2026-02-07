import json
import socket

def send_request(ip, port, request):
    # Envoie une requête JSON à un serveur et retourne la réponse
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    s.send(json.dumps(request).encode())
    response = json.loads(s.recv(4096).decode())
    s.close()
    return response