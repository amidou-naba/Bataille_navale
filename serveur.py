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


