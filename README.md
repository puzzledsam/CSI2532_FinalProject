# CSI2532 Projet Final

## Prérequis
- Python 3.9 ou plus récent
- [Outils psql](https://www.postgresql.org/download/)

## Comment utiliser
1. Après avoir téléchargé le code de ce répertoire GitHub, vous devez installer les packages Python indiqués dans le fichier "requirements.txt" ou utilisez `pip install -r requirements.txt` pour les installer automatiquement
2. Modifiez le fichier "config.py.example" avec les détails de la base de données PostgreSQL que vous voulez utiliser
  - Vous pouvez utiliser votre base de données uOttawa ou une base de données locale
  - Après avoir modifié le fichier, renommez le tout simplement à "config.py"
3. Exécutez `python init_db.py` pour tester votre connection à la base de données et initialiser les données de l'application
  - Seulement nécessaire la première fois, sinon vos données seront **effacées et remises aux valeurs par défaut**
4. Exécutez `python app.py` pour démarrer l'application (elle s'exécutera jusqu'à ce que vous appuyez CTRL + C dans votre terminal)
5. Visitez `http://localhost:7832` ou [cliquez ici](http://localhost:7832) dans votre navigateur pour utiliser l'application

## Informations supplémentaires
- Les utilisateurs ne sont pas sécurisés dans la base de données, n'utilisez donc pas vos vrais mot de passes
- Les réceptionnistes sont associées à leur succursales et peuvent seulement fixer des rendez-vous dans leur propre succursale

## Comptes pré-définis
### Patient
- Username: johndoe
- Password: password

### Réceptioniste
- Username: testuser
- Password: password

### Dentiste/Hygiéniste
- Username: testdentist
- Password: password
