import socket
import time
def create_empty_grid():
    """Crée une grille vide 10x10."""
    return [[" " for _ in range(10)] for _ in range(10)]
def print_grid(grid):
    """Affiche la grille formatée."""
    letters = "A B C D E F G H I J"
    print("\n    " + letters)
    for i in range(10):
        row = " ".join(grid[i])
        index = str(i + 1).ljust(2)
        print(f"{index} {row}")
    print("    " + letters + "\n")
def ask_for_shot():
    """Demande colonne et ligne séparément."""
    while True:
        col = input("Quelle colonne (A-J) ? ").upper()
        if col in "ABCDEFGHIJ":
            col_index = ord(col) - ord("A")
            break
        print(" Colonne invalide.")

    while True:
        row = input("Quelle ligne (1-10) ? ")
        if row.isdigit() and 1 <= int(row) <= 10:
            row_index = int(row) - 1
            break
        print(" Ligne invalide.")

    return row_index, col_index
def start_client(server_ip, server_port=7777):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connecter_au_serveur():
        """Tente une connexion au serveur."""
        try:
            client.connect((server_ip, server_port))
            print(" Connexion réussie au serveur.")
            return True
        except socket.error as e:
            print(f" Erreur de connexion : {e}")
            return False

    # Tentative initiale
    if not connecter_au_serveur():
        print("Nouvel essai dans 15 secondes...")
        time.sleep(15)
        if not connecter_au_serveur():
            print(" Impossible de se connecter.")
            return

