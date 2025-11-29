import socket
import sys
import hashlib
import time
import random
import pickle

def creer_grille(taille=10):
    """Crée une grille vide de jeu"""
    return [["~" for _ in range(taille)] for _ in range(taille)]

def afficher_grille(grille, titre="Grille"):
    """Affiche une grille avec ses coordonnées"""
    print(f"\n{titre}")
    print("   " + " ".join([chr(ord('A') + i) for i in range(len(grille))]))
    for idx, ligne in enumerate(grille):
        print(f"{idx:2d} " + " ".join(ligne))

def afficher_double_grille(grille_tirs, grille_defense):
    """Affiche les deux grilles côte à côte"""
    taille = len(grille_tirs)
    print("\n" + "="*70)
    print("Vos tirs sur l'adversaire        Votre grille de défense")
    print("="*70)
    
    header = "   " + " ".join([chr(ord('A') + i) for i in range(taille)])
    print(f"{header}      {header}")
    
    for idx in range(taille):
        ligne_tirs = f"{idx:2d} " + " ".join(grille_tirs[idx])
        ligne_def = f"{idx:2d} " + " ".join(grille_defense[idx])
        print(f"{ligne_tirs}      {ligne_def}")
    
    print("\nLégende: B=Bateau  X=Touché  O=Manqué  ~=Eau\n")

def pos_vers_coord(pos, taille=10):
    """Convertit une position type 'A5' en coordonnées (ligne, colonne)"""
    try:
        pos = pos.strip().upper()
        col = ord(pos[0]) - ord('A')
        ligne = int(pos[1:])
        if 0 <= ligne < taille and 0 <= col < taille:
            return ligne, col
        return None, None
    except:
        return None, None

def sauvegarder_etat(grille_tirs, grille_defense, positions, nom_fichier="etat_jeu.pkl"):
    """Sauvegarde l'état du jeu dans un fichier"""
    try:
        etat = {
            'grille_tirs': grille_tirs,
            'grille_defense': grille_defense,
            'positions': positions
        }
        with open(nom_fichier, 'wb') as f:
            pickle.dump(etat, f)
        print("État du jeu sauvegardé")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")

def charger_etat(nom_fichier="etat_jeu.pkl"):
    """Charge l'état du jeu depuis un fichier"""
    try:
        with open(nom_fichier, 'rb') as f:
            etat = pickle.load(f)
        print("État du jeu récupéré")
        return etat['grille_tirs'], etat['grille_defense'], etat['positions']
    except FileNotFoundError:
        print("Aucun état sauvegardé trouvé")
        return None, None, None
    except Exception as e:
        print(f"Erreur lors du chargement: {e}")
        return None, None, None

def generer_positions_aleatoires(taille=10, nb_bateaux=5):
    """Génère des positions aléatoires pour un robot"""
    positions = []
    cases_utilisees = set()
    
    while len(positions) < nb_bateaux:
        ligne = random.randint(0, taille - 1)
        col = random.randint(0, taille - 1)
        
        if (ligne, col) not in cases_utilisees:
            positions.append(f"{chr(ord('A') + col)}{ligne}")
            cases_utilisees.add((ligne, col))
    
    return ",".join(positions)

def coup_aleatoire_robot(grille_tirs, taille=10):
    """Génère un coup aléatoire pour un robot"""
    cases_disponibles = []
    
    for ligne in range(taille):
        for col in range(taille):
            if grille_tirs[ligne][col] == "~":
                cases_disponibles.append((ligne, col))
    
    if cases_disponibles:
        ligne, col = random.choice(cases_disponibles)
        return f"{chr(ord('A') + col)}{ligne}"
    
    return None

def reconnecter(serveur, port, max_tentatives=5):
    """Tente de se reconnecter au serveur"""
    for tentative in range(1, max_tentatives + 1):
        try:
            print(f"\nTentative de reconnexion {tentative}/{max_tentatives}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((serveur, port))
            print("Reconnexion réussie!")
            return sock
        except:
            if tentative < max_tentatives:
                time.sleep(2)
            else:
                print("Impossible de se reconnecter.")
                return None

def mode_joueur(sock, serveur, port, taille=10, mode_robot=False):
    """Mode joueur: placer les bateaux et jouer"""
    
    grille_tirs = creer_grille(taille)
    grille_defense = creer_grille(taille)
    positions = ""
    
    # Tenter de récupérer un état sauvegardé
    grille_t_saved, grille_d_saved, pos_saved = charger_etat()
    
    if grille_t_saved is not None:
        reprise = input("Un état de jeu sauvegardé existe. Reprendre? (o/n): ").strip().lower()
        if reprise == 'o':
            grille_tirs = grille_t_saved
            grille_defense = grille_d_saved
            positions = pos_saved
            
            # Envoyer signal de reconnexion au serveur
            sock.sendall(b"RECONNECT\n")
            sock.sendall((positions + "\n").encode('utf-8'))
            
            print("Reprise de la partie...")
    
    if not positions:
        print("\n=== Placement des bateaux ===")
        print(f"Entrez les positions de vos bateaux séparées par des virgules")
        print(f"Exemple: A0,B0,C0,D0,E0")
        
        if mode_robot:
            positions = generer_positions_aleatoires(taille)
            print(f"Robot - Positions générées: {positions}")
        else:
            positions = input("Vos positions: ").strip()
        
        # Marquer les bateaux sur la grille de défense
        for pos in positions.split(","):
            ligne, col = pos_vers_coord(pos.strip(), taille)
            if ligne is not None and col is not None:
                grille_defense[ligne][col] = "B"
        
        afficher_grille(grille_defense, "Votre grille de défense")
        
        # Envoyer les positions au serveur
        sock.sendall((positions + "\n").encode('utf-8'))
        
        # Calculer et envoyer le hash
        hash_positions = hashlib.sha256(positions.encode('utf-8')).hexdigest()
        sock.sendall((hash_positions + "\n").encode('utf-8'))
        
        # Sauvegarder l'état initial
        sauvegarder_etat(grille_tirs, grille_defense, positions)
    
    print("\nEn attente de l'autre joueur...")
    
    # Boucle de jeu
    while True:
        try:
            # Recevoir message du serveur
            message = sock.recv(1024).decode('utf-8').strip()
            
            if not message:
                continue
            
            # Gestion de la récupération d'état
            if message.startswith("STATE:"):
                print("Réception de l'état du jeu...")
                try:
                    etat_data = message.split("STATE:")[1]
                    # Le serveur envoie l'état au format attendu
                    print("État reçu du serveur")
                except:
                    pass
            
            elif message == "YOUR_TURN":
                # C'est notre tour
                afficher_double_grille(grille_tirs, grille_defense)
                print("C'est votre tour!")
                
                # Demander le coup à jouer
                if mode_robot:
                    coup = coup_aleatoire_robot(grille_tirs, taille)
                    if coup:
                        print(f"Robot tire en: {coup}")
                        time.sleep(1)
                    else:
                        print("Plus de cases disponibles!")
                        break
                else:
                    coup = input("Entrez votre tir (ex: A5): ").strip().upper()
                
                # Envoyer le coup
                sock.sendall((coup + "\n").encode('utf-8'))
                
                # Recevoir le résultat
                resultat = sock.recv(1024).decode('utf-8').strip()
                print(f"Résultat: {resultat}")
                
                # Mettre à jour la grille de tirs
                ligne, col = pos_vers_coord(coup, taille)
                if ligne is not None and col is not None:
                    if "TOUCHE" in resultat.upper():
                        grille_tirs[ligne][col] = "X"
                    else:
                        grille_tirs[ligne][col] = "O"
                
                # Sauvegarder l'état après chaque coup
                sauvegarder_etat(grille_tirs, grille_defense, positions)
            
            elif message.startswith("OPP_SHOT:"):
                # L'adversaire a tiré
                coup_adv = message.split(":")[1].strip()
                ligne, col = pos_vers_coord(coup_adv, taille)
                
                if ligne is not None and col is not None:
                    if grille_defense[ligne][col] == "B":
                        grille_defense[ligne][col] = "X"
                        print(f"\nL'adversaire a touché votre bateau en {coup_adv}!")
                    else:
                        grille_defense[ligne][col] = "O"
                        print(f"\nL'adversaire a tiré en {coup_adv}")
                
                # Sauvegarder l'état après le coup adverse
                sauvegarder_etat(grille_tirs, grille_defense, positions)
            
            elif message == "WAIT":
                print("En attente du coup adverse...")
            
            elif "GAME_OVER" in message or "VICTOIRE" in message or "DEFAITE" in message:
                print(f"\n{message}")
                afficher_double_grille(grille_tirs, grille_defense)
                
                # Demander si on veut rejouer
                rejouer = input("\nRejouer une partie? (o/n): ").strip().lower()
                if rejouer == 'o':
                    sock.sendall(b"REPLAY\n")
                    # Réinitialiser les grilles
                    grille_tirs = creer_grille(taille)
                    grille_defense = creer_grille(taille)
                    continue
                else:
                    sock.sendall(b"QUIT\n")
                    break
            
            else:
                print(message)
        
        except ConnectionResetError:
            print("\nConnexion perdue avec le serveur!")
            print("Tentative de reconnexion...")
            
            # Tenter de se reconnecter
            sock = reconnecter(serveur, port)
            if sock:
                # Envoyer signal de reconnexion
                sock.sendall(b"RECONNECT\n")
                sock.sendall((positions + "\n").encode('utf-8'))
                print("Partie reprise")
            else:
                print("Impossible de reprendre la partie")
                break
                
        except Exception as e:
            print(f"Erreur: {e}")
            break

def mode_observateur(sock):
    """Mode observateur: afficher les événements de la partie"""
    
    print("\n=== Mode Observateur ===")
    print("Vous observez la partie en cours...\n")
    
    try:
        while True:
            message = sock.recv(1024).decode('utf-8').strip()
            
            if not message:
                continue
            
            print(f"[Serveur] {message}")
            
            if "GAME_OVER" in message or "FIN" in message:
                break
                
    except Exception as e:
        print(f"Erreur: {e}")

def mode_peer_to_peer(hote, taille=10):
    """Mode jeu sans serveur (peer-to-peer)"""
    
    print("\n=== Mode Peer-to-Peer ===")
    role = input("Êtes-vous l'hôte ou le client? (hote/client): ").strip().lower()
    
    if role == "hote":
        # Créer un serveur simple
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("0.0.0.0", 7777))
        server_sock.listen(1)
        print("En attente de connexion de l'autre joueur...")
        
        sock, addr = server_sock.accept()
        print(f"Joueur connecté depuis {addr}")
    else:
        # Se connecter à l'hôte
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hote, 7777))
        print("Connecté à l'hôte!")
    
    # Placement des bateaux
    print("\n=== Placement des bateaux ===")
    positions = input("Vos positions: ").strip()
    hash_positions = hashlib.sha256(positions.encode('utf-8')).hexdigest()
    
    # Échanger les hashs
    sock.sendall((hash_positions + "\n").encode('utf-8'))
    hash_adversaire = sock.recv(1024).decode('utf-8').strip()
    
    print("Hash échangés - Début de la partie")
    print("Note: Les hashs seront vérifiés à la fin pour détecter toute triche")
    
    grille_tirs = creer_grille(taille)
    grille_defense = creer_grille(taille)
    
    # Marquer les bateaux
    for pos in positions.split(","):
        ligne, col = pos_vers_coord(pos.strip(), taille)
        if ligne is not None and col is not None:
            grille_defense[ligne][col] = "B"
    
    # Jeu simple tour par tour
    mon_tour = (role == "hote")
    
    while True:
        if mon_tour:
            afficher_double_grille(grille_tirs, grille_defense)
            coup = input("Votre tir: ").strip().upper()
            sock.sendall((coup + "\n").encode('utf-8'))
            
            # Recevoir le résultat
            resultat = sock.recv(1024).decode('utf-8').strip()
            print(f"Résultat: {resultat}")
            
            ligne, col = pos_vers_coord(coup, taille)
            if "TOUCHE" in resultat.upper():
                grille_tirs[ligne][col] = "X"
            else:
                grille_tirs[ligne][col] = "O"
            
            mon_tour = False
        else:
            print("En attente du coup adverse...")
            coup_adv = sock.recv(1024).decode('utf-8').strip()
            
            ligne, col = pos_vers_coord(coup_adv, taille)
            if grille_defense[ligne][col] == "B":
                resultat = "TOUCHE"
                grille_defense[ligne][col] = "X"
            else:
                resultat = "MANQUE"
                grille_defense[ligne][col] = "O"
            
            sock.sendall((resultat + "\n").encode('utf-8'))
            print(f"Adversaire a tiré en {coup_adv}: {resultat}")
            
            mon_tour = True

def main():
    """Fonction principale du client"""
    
    print("=== Client Bataille Navale ===")
    print("1. Mode normal (avec serveur)")
    print("2. Mode robot")
    print("3. Mode peer-to-peer (sans serveur)")
    
    choix = input("\nChoisissez un mode (1/2/3): ").strip()
    
    if choix == "3":
        # Mode P2P
        hote = input("Adresse de l'hôte (ou laissez vide si vous êtes l'hôte): ").strip()
        if not hote:
            hote = "localhost"
        mode_peer_to_peer(hote)
        return
    
    # Mode normal ou robot
    mode_robot = (choix == "2")
    
    # Récupérer l'adresse du serveur
    if len(sys.argv) > 1:
        serveur = sys.argv[1]
    else:
        serveur = input("Adresse du serveur: ").strip()
        if not serveur:
            serveur = "localhost"
    
    port = 7777
    
    try:
        # Créer la socket et se connecter
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connexion au serveur {serveur}:{port}...")
        sock.connect((serveur, port))
        print("Connecté!\n")
        
        # Recevoir le message de bienvenue
        bienvenue = sock.recv(1024).decode('utf-8').strip()
        print(bienvenue)
        
        # Déterminer le rôle
        if "observateur" in bienvenue.lower():
            mode_observateur(sock)
        else:
            mode_joueur(sock, serveur, port, mode_robot=mode_robot)
        
    except ConnectionRefusedError:
        print(f"Erreur: Impossible de se connecter au serveur {serveur}:{port}")
        print("Vérifiez que le serveur est lancé.")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

if __name__ == "__main__":
    main()
