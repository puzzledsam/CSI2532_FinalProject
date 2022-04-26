import psycopg2
import config as appConfig

conn = psycopg2.connect(
        host=appConfig.Config.DB_HOST,
        port=appConfig.Config.DB_PORT,
        database=appConfig.Config.DB_NAME,
        user=appConfig.Config.DB_USERNAME,
        password=appConfig.Config.DB_PASSWORD)

# Open a cursor to perform database operations
cur = conn.cursor()

# Create tables and initialize some default values
cur.execute('DROP TABLE IF EXISTS utilisateurs;')
cur.execute('CREATE TABLE utilisateurs (id serial PRIMARY KEY,'
                'username varchar NOT NULL UNIQUE,'
                'password varchar NOT NULL,'
                'type_utilisateur varchar NOT NULL);'
                )

cur.execute('INSERT INTO utilisateurs (username, password, type_utilisateur)'
                'VALUES (%s, %s, %s)',
                ('testuser',
                'password',
                'admin')
                )

cur.execute('DROP TABLE IF EXISTS employes;')
cur.execute('CREATE TABLE employes (employe_id serial PRIMARY KEY,'
            'nom varchar NOT NULL,'
            'adresse varchar(200) NOT NULL,'
            'role varchar NOT NULL,'
            'type_employe varchar NOT NULL,'
            'SSN integer NOT NULL,'
            'salaire decimal(8,2) NOT NULL);')

cur.execute('DROP TABLE IF EXISTS patients;')
cur.execute('CREATE TABLE patients (patient_id serial PRIMARY KEY,'
                'nom varchar NOT NULL,'
                'sexe varchar NOT NULL,'
                'assurance varchar,'
                'SSN integer NOT NULL,'
                'email varchar NOT NULL,'
                'date_naissance date NOT NULL,'
                'telephone integer NOT NULL,'
                'addresse varchar(200) NOT NULL);'
                )

cur.execute('DROP TABLE IF EXISTS succursales;')
cur.execute('CREATE TABLE succursales (ville varchar PRIMARY KEY,'
                'directeur varchar,'
                'receptioniste varchar);')

cur.execute('DROP TABLE IF EXISTS traitements;')
cur.execute('CREATE TABLE traitements (rdv_id int NOT NULL,'
                'type_traitement varchar NOT NULL,'
                'dents varchar NOT NULL,'
                'commentaires varchar(200));')

cur.execute('DROP TABLE IF EXISTS procedures;')
cur.execute('CREATE TABLE procedures (patient_id integer NOT NULL,'
                'date date NOT NULL,'
                'code_procedure varchar NOT NULL,'
                'type_procedure varchar NOT NULL,'
                'quantite_procedure integer NOT NULL);')

cur.execute('DROP TABLE IF EXISTS frais;')
cur.execute('CREATE TABLE frais (indicateur varchar NOT NULL,' # Not sure what this is, an ID of some sort?
                'procedure varchar NOT NULL,'
                'code_frais varchar NOT NULL,'
                'frais decimal(10,2) NOT NULL);')

cur.execute('DROP TABLE IF EXISTS assurance;')
cur.execute('CREATE TABLE assurance (reclamation_id serial PRIMARY KEY, '
                'patient_id integer NOT NULL,'
                'paiement_id integer NOT NULL);')

conn.commit()

cur.close()
conn.close()

print("DB init complete.")