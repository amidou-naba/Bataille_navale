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
 if player_id <= 1:
            # Attendre que le joueur joue son tour
            while not game_paused:
                if player_turn == player_id:
                    # Si c'est son tour et que c'est un joueur, demander un coup
                    client_socket.send("C'est votre tour, entrez un coup (ex: A1): ".encode())
                    coup = client_socket.recv(1024).decode()
                    print(f"Joueur {player_id + 1} a joué le coup: {coup}")

                    # Changer de joueur pour le prochain tour
                    player_turn = 1 - player_id
                    notify_players(f"Joueur {player_id + 1} a joué: {coup}")

                    client_socket.send(f"Votre coup {coup} a été joué.".encode())

                else:
                    # Si ce n'est pas son tour, le serveur ne doit pas faire de répétitions inutiles
                    time.sleep(0.5)  # Attendre un peu avant de vérifier à nouveau

        else:
            # Les observateurs attendent passivement les notifications du serveur
            while not game_paused:
                time.sleep(15)
                  except Exception as e:
        print(f"Erreur avec le joueur {player_id + 1}: {e}")
        # En cas de déconnexion, mettre la partie en pause
        game_paused = True
        notify_players(f"Le joueur {player_id + 1} a été déconnecté. La partie est en pause.")
        reconnect(client_socket, player_id)

    finally:
        client_socket.close()
# Fonction pour notifier tous les joueurs et observateurs
def notify_players(message):
    # Notifier tous les joueurs
    for player in players.values():
        if player:
            try:
                player.send(message.encode())
            except:
                pass
    # Notifier tous les observateurs
    for observer in observers:
        try:
            observer.send(message.encode())
        except:
            pass

# Fonction pour gérer la reconnexion d'un joueur
def reconnect(client_socket, player_id):
    global game_paused
    print(f"Attente de reconnexion pour le joueur {player_id + 1}...")
    time.sleep(5)  # Attente avant la reconnexion

    while True:
        try:
            # Tentative de reconnexion sur le même port
            client_socket.connect(('localhost', 7777))  # Reconnexion sur le même serveur
            client_socket.send(f"Reconnexion réussie, vous êtes le joueur {player_id + 1}.".encode())
            game_paused = False  # Relancer le jeu
            players[player_id] = client_socket  # Ajouter le joueur reconnecté
            print(f"Le joueur {player_id + 1} s'est reconnecté.")
            notify_players(f"Le joueur {player_id + 1} s'est reconnecté, la partie reprend.")
            break
        except:
            print(f"Erreur de reconnexion pour le joueur {player_id + 1}, nouvelle tentative dans 5 secondes...")
            time.sleep(5)
