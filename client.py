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

