import socket
import time

def connection_to_server(ip, port):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))
            print("Connexion réussie au serveur !")
            return client_socket
        except socket.error:
            print("Erreur de connexion, nouvelle tentative dans 5 secondes...")
            time.sleep(5)


