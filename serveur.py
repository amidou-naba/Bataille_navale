import socket
import threading
import time

# Variables globales
clients = []  # Liste des clients (joueurs + observateurs)
players = {0: None, 1: None}  # Dictionnaire des joueurs, clé = 0 ou 1
observers = []  # Liste des observateurs
player_turn = 0  # Le joueur 1 commence
game_paused = False  # Indicateur de pause de la partie
batailles = {"player_1": [], "player_2": []}  # Positionnement des bateaux

def handle_client(client_socket, player_id):
    global player_turn, game_paused, batailles

    try:
        # Envoyer un message d'accueil au joueur
        if player_id <= 1:
            client_socket.send(f"Bienvenue, vous êtes le joueur {player_id + 1}. Entrez la position de vos bateaux (ex: A1): ".encode())
            bateaux_positions = client_socket.recv(1024).decode()
            batailles[f"player_{player_id + 1}"] = bateaux_positions.split(',')
            print(f"Joueur {player_id + 1} a positionné ses bateaux: {bateaux_positions}")
        else:
            client_socket.send("Bienvenue, vous êes un observateur. Vous ne pouvez pas jouer.".encode())
