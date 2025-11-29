import socket
import time

# -----------------------------
#  GRILLE BATAILLE NAVALE
# -----------------------------

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
        print("❌ Colonne invalide.")

    while True:
        row = input("Quelle ligne (1-10) ? ")
        if row.isdigit() and 1 <= int(row) <= 10:
            row_index = int(row) - 1
            break
        print("❌ Ligne invalide.")

    return row_index, col_index


# -----------------------------
#  CLIENT PRINCIPAL
# -----------------------------

def start_client(server_ip, server_port=7777):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connecter_au_serveur():
        """Tente une connexion au serveur."""
        try:
            client.connect((server_ip, server_port))
            print("✔ Connexion réussie au serveur.")
            return True
        except socket.error as e:
            print(f"❌ Erreur de connexion : {e}")
            return False

    # Tentative initiale
    if not connecter_au_serveur():
        print("Nouvel essai dans 15 secondes...")
        time.sleep(15)
        if not connecter_au_serveur():
            print("❌ Impossible de se connecter.")
            return

    # Message de bienvenue
    message = client.recv(1024).decode()
    print(message)

    # ---------------------------------
    #         MODE JOUEUR
    # ---------------------------------
    if "joueur" in message.lower():

        # Grille du joueur
        grid = create_empty_grid()

        # Envoyer positions des bateaux
        bateaux_positions = input("Entrez la position de vos bateaux (ex: A1, B2, C3): ")
        client.send(bateaux_positions.encode())

        while True:
            try:
                # Message du serveur (tour de jeu ou update)
                msg = client.recv(1024).decode()
                print(msg)

                # Vérification que c'est le tour du joueur
                if "C'est votre tour" in msg:

                    print("\n===== VOTRE GRILLE =====")
                    print_grid(grid)

                    # Demander un tir
                    row, col = ask_for_shot()

                    coup = f"{chr(col + ord('A'))}{row + 1}"
                    client.send(coup.encode())

                    # Réponse du serveur
                    result = client.recv(1024).decode()
                    print(result)

                    # Marquer le tir sur la grille
                    grid[row][col] = "X"

            except socket.error as e:
                print(f"⚠ Connexion perdue : {e}")
                print("Tentative de reconnexion dans 15 secondes...")
                client.close()
                time.sleep(15)

                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if connecter_au_serveur():
                    print("✔ Reconnexion réussie.")
                    continue
                else:
                    print("❌ Reconnexion impossible.")
                    break

    # ---------------------------------
    #        MODE OBSERVATEUR
    # ---------------------------------
    else:
        print("🔍 Mode observateur activé.")
        while True:
            try:
                message = client.recv(1024).decode()
                print(f"[OBS] {message}")
            except socket.error as e:
                print(f"Connexion perdue : {e}")
                print("Réessai dans 15 secondes...")
                client.close()
                time.sleep(15)

                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if connecter_au_serveur():
                    print("✔ Reconnexion réussie.")
                    continue
                else:
                    print("❌ Impossible de se reconnecter.")
                    break


# -----------------------------
#  LANCEMENT
# -----------------------------

if __name__ == "__main__":
    server_ip = input("Entrez l'adresse du serveur : ")
    start_client(server_ip)

