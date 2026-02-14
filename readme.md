Mini-projet d'un système de fichier distribués
- .env:
    fichier de configuration fournissant:
        - le serveur de métadonnées avec "METADATA_SERVER=adresse_serveur:port"
        - les serveurs de stockages avec "STORAGE_SERVERS=adresse_server1:port1;adresse_server2:port2 etc..."
- client.py: commande de lancement "python client.py"
    un shell se lance permettant de:
        - lister les fichier avec "list" ou "ls"
        - créer un fichier avec "create <nom_fichier> [contenu]"
        - écrire un fichier (concatener a la fin du fichier) avec "write <nom_fichier> [contenu] 
        - lire un fichier avec "read <nom_fichier>"
        - supprimer un fichir avec "delete <nom_fichier>" ou "del <nom_fichier>"
        - voir les commandes possibles avec "help"
        - sortir avec "exit"
    si une erreur se produit un code erreur est retourné:
        - 401: fichier ouvert par un autre client
        - 404: fichier introuvable
        - 400: Erreur inconnu

- metadata_server.py: commande de lancement "python metadata_server.py"
    serveur centralisé gérant les métadonnées des fichiers:
        - choix de l'emplacement pour les nouveaux fichiers
        - enregistrement des fichiers et leurs emplacements
        - gestion des verrous pour éviter les accès concurrents
        - synchronisation avec les serveurs de stockage
    au lancement du serveur de metadonnées, ce dernier liste les fichiers stocké dans les serveurs de stockage

- storage_server.py: commande de lancement "python storage_server.py <numero_port>"
    serveur de stockage distribuant les données des fichiers:
        - stockage physique des fichiers dans le repertoire "data_numero_port"
        - lecture et écriture des données
        - nettoyage des fichiers supprimés