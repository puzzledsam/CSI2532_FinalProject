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

# Create tables and fill them with default values
cur.execute('DROP TABLE IF EXISTS utilisateurs;')
cur.execute('CREATE TABLE utilisateurs (id serial PRIMARY KEY UNIQUE,'
                'username varchar NOT NULL UNIQUE,'
                'password varchar NOT NULL,'
                'role varchar(10) NOT NULL);'
                )

cur.execute('INSERT INTO utilisateurs (username, password, role)'
                'VALUES (%s, %s, %s)',
                ('testuser',
                'password',
                'admin')
                )

cur.execute('CREATE TABLE patients (patient_id serial PRIMARY KEY UNIQUE,'
                'nom varchar NOT NULL,'
                'sexe varchar NOT NULL,'
                'assurance varchar,'
                'SSN integer NOT NULL,'
                'email varchar NOT NULL,'
                'date_naissance date NOT NULL,'
                'telephone integer NOT NULL,'
                'address varchar(200) NOT NULL);'
                )

conn.commit()

cur.close()
conn.close()

print("DB init complete.")