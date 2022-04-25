# CSI2532 Projet Final

## Comment utiliser
1. Après avoir téléchargé le code de ce répertoire GitHub, vous devez installer les packages Python indiqués dans le fichier "requirements.txt" ou utilisez `pip install -r requirements.txt` pour les installer automatiquement
2. Modifiez le fichier "config.py.example" avec les détails de la base de données PostgreSQL auquel vous voulez utiliser
  * Vous pouvez utiliser votre base de données uOttawa ou une base de données locale
  * Après avoir modifié le fichier, renommez le tout simplement à "config.py"
3. Exécutez `python init_db.py` pour tester votre connection à la base de données et initialiser les données de l'application
4. Exécutez `python app.py` pour démarrer l'application (elle s'exécutera jusqu'à ce que vous appuyez CTRL + C dans votre terminal)
5. Visitez `http://localhost:7832` ou [cliquez ici](http://localhost:7832) dans votre navigateur pour utiliser l'application

## Informations supplémentaires
- L'application nécessite Python 3
- Les utilisateurs ne sont pas sécurisés dans la base de données, n'utilisez donc pas vos vrais mot de passes
