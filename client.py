import socket
import time

#Added server connection function with error handling
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
#Function to manage reconnection in case of disconnection
def wait_connection(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)  # Recevoir des données
            if not data:
                break  # Si la connexion est fermée
        except socket.error:
            print("Connexion perdue, tentatives de reconnexion...")
            reconnecter(client_socket)
            break

#Reconnect function
def reconnect(client_socket):
    client_socket.close()
    client_socket = connecter_au_serveur('adresse_serveur', 12345)  # Remplace par l'adresse du serveur
    return client_socket


