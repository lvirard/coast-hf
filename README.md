# coast-hf
An app to easily visualize oceanographic data from Coast-HF network


Project developped during a 3 weeks internship in LOPS-Ifremer
In 3 STEPS :

Step 1 : design the app with streamlit and fictive data --> completed

Step 2 : Insert real data --> completed

Step 3 : Host online & with daily pushed updated data --> ongoing
Work online, but not yet with pushed updated data.
http://data.coast-hf.fr

The files accesibles from the repository are the Step 2 files.
The app is runned by a terminal using the command :
streamlit run accueil.py


Recommandations pour la suite (FR) : 
- Vérifier que le certificat SSL fonctionne correctement
- Créer un programme qui permet d’envoyer quotidiennement le fichier LATEST pour toutes les bouées sur le VPS.
- rajouter une période annuelle ? 
- rajouter la hauteur d’eau sur les graphs pour comparer avec les marées ? 
- créer un lien depuis le site coast-hf pour accéder à l’application.
