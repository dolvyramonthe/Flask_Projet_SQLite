import sqlite3
import os
from pathlib import Path

# Configuration
DB_NAME = 'database.db'
SCHEMA_FILE = 'schema.sql'
INSERT_CLIENT_SQL = "INSERT INTO clients (created, nom, prenom, adresse) VALUES (strftime('%s', 'now'), ?, ?, ?)"

def create_database():
    """Crée et initialise la base de données"""
    try:
        # Vérification de l'existence du fichier de schéma
        if not Path(SCHEMA_FILE).exists():
            raise FileNotFoundError(f"Le fichier de schéma {SCHEMA_FILE} n'existe pas")

        # Connexion à la base de données
        connection = sqlite3.connect(DB_NAME)
        connection.row_factory = sqlite3.Row

        # Exécution du script SQL de création de schéma
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as schema_file:
            connection.executescript(schema_file.read())

        # Données de test
        clients = [
            ('DUPONT', 'Emilie', '123, Rue des Lilas, 75001 Paris'),
            ('LEROUX', 'Lucas', '456, Avenue du Soleil, 31000 Toulouse'),
            ('MARTIN', 'Amandine', '789, Rue des Érables, 69002 Lyon'),
            ('TREMBLAY', 'Antoine', '1010, Boulevard de la Mer, 13008 Marseille'),
            ('LAMBERT', 'Sarah', '222, Avenue de la Liberté, 59000 Lille'),
            ('GAGNON', 'Nicolas', '456, Boulevard des Cerisiers, 69003 Lyon'),
            ('DUBOIS', 'Charlotte', '789, Rue des Roses, 13005 Marseille'),
            ('LEFEVRE', 'Thomas', '333, Rue de la Paix, 75002 Paris'),
        ]

        # Insertion des données avec gestion des erreurs
        with connection:
            cursor = connection.cursor()
            cursor.executemany(INSERT_CLIENT_SQL, clients)
            
        print(f"Base de données '{DB_NAME}' créée avec succès avec {len(clients)} clients.")
        
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        raise
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    create_database()
