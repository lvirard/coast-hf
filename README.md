# coast-hf
An app to easily visualize oceanographic data from Coast-HF network

Project In 3 STEPS :

Step 1 : design the app with streamlit and fictive data --> completed

Step 2 : Insert real data --> completed

Step 3 : host online & with daily pushed updated data --> ongoing
Work online, but not yet with pushed updated data.
http://app.coast-hf.fr

The files accesibles from the repository are the Step 2 files.
The app is runned by a terminal using the command :
streamlit run accueil.py


Recommandations pour la suite (FR) : 
- trouver la façon de lire des fichiers sur le VPS qui ne sont pas dans le container
- Créer un programme qui permet d’envoyer quotidiennement le fichier LATEST pour toutes les bouées sur le VPS.
- Régler les erreurs d’affichage dans le cas ou il n’y a pas de données disponibles (rajouter des try except dans le code)
      exemples d’erreurs testées qui apparaissent en rouge :
            - lorsqu’il n’y a pas de fichier associé à la bouée
            - lorsqu’il n’y a pas de données associées au paramètre choisi
- trouver le moyen d’enlever la navigation entre les pages dans le menu en haut à gauche (les onglets avec le nom des pages).
- rajouter une période annuelle ? 
- rajouter la hauteur d’eau sur les graphs pour comparer avec les marées ? 
- modifier l’onglet informations pour n’y afficher que ce que l’on veut.
- créer un lien depuis le site coast-hf pour accéder à l’application.
