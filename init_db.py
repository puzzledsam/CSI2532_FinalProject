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
cur.execute('DROP TABLE IF EXISTS assurance;')
cur.execute('DROP TABLE IF EXISTS frais;')
cur.execute('DROP TABLE IF EXISTS procedures;')
cur.execute('DROP TABLE IF EXISTS traitements;')
cur.execute('DROP TABLE IF EXISTS rendezvous;')
cur.execute('DROP TABLE IF EXISTS employes;')
cur.execute('DROP TABLE IF EXISTS patients;')

cur.execute('CREATE TABLE patients (patient_id serial PRIMARY KEY,'
                'nom varchar NOT NULL,'
                'sexe varchar NOT NULL,'
                'assurance varchar,'
                'SSN int NOT NULL,'
                'email varchar NOT NULL,'
                'date_naissance date NOT NULL,'
                'telephone bigint NOT NULL,'
                'addresse varchar(200) NOT NULL);'
                )

cur.execute('INSERT INTO patients (nom, sexe, SSN, email, date_naissance, telephone, addresse)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                ('John Doe',
                'Homme',
                123456789,
                'email@email.com',
                '1999-07-23',
                6136136134,
                '123 rue Chemin')
                )

cur.execute('DROP TABLE IF EXISTS succursales;')
cur.execute('CREATE TABLE succursales (succursale_id serial PRIMARY KEY,'
                'ville varchar NOT NULL UNIQUE,'
                'directeur varchar,'
                'receptioniste varchar);')

cur.execute("INSERT INTO succursales (ville) VALUES ('Ottawa');")
cur.execute("INSERT INTO succursales (ville) VALUES ('Toronto');")
cur.execute("INSERT INTO succursales (ville) VALUES ('Montreal');")
cur.execute("INSERT INTO succursales (ville) VALUES ('Edmonton');")
cur.execute("INSERT INTO succursales (ville) VALUES ('Winnipeg');")
cur.execute("INSERT INTO succursales (ville) VALUES ('Regina');")

cur.execute('CREATE TABLE employes (employe_id serial PRIMARY KEY,'
                'succursale_id int NOT NULL,'
                'nom varchar NOT NULL,'
                'adresse varchar(200) NOT NULL,'
                'role varchar NOT NULL,'
                'type_employe varchar NOT NULL,'
                'SSN int NOT NULL,'
                'salaire decimal(8,2) NOT NULL,'
                'FOREIGN KEY (succursale_id) REFERENCES succursales(succursale_id));')

cur.execute('INSERT INTO employes (succursale_id, nom, adresse, role, type_employe, SSN, salaire)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (1,
                'Gregoire Tremblay',
                '739 rue Main',
                'Réceptioniste',
                'receptionist',
                890455243,
                16.80)
                )

cur.execute('INSERT INTO employes (succursale_id, nom, adresse, role, type_employe, SSN, salaire)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (1,
                'Ginette Langlois',
                '834 rue Desrosiers',
                'Hygiéniste',
                'dentist',
                348932580,
                32.50)
                )

cur.execute('CREATE TABLE rendezvous (rdv_id serial PRIMARY KEY,'
                'patient_id int NOT NULL,'
                'dentist_id int NOT NULL,'
                'succursale_id int NOT NULL,'
                'date_rdv timestamp NOT NULL,'
                'qty_procedure int NOT NULL,'
                'FOREIGN KEY (patient_id) REFERENCES patients(patient_id),'
                'FOREIGN KEY (dentist_id) REFERENCES employes(employe_id),'
                'FOREIGN KEY (succursale_id) REFERENCES succursales(succursale_id));')

cur.execute('CREATE TABLE traitements (traitement_id serial PRIMARY KEY,'
                'rdv_id int NOT NULL,'
                'type_traitement varchar NOT NULL,'
                'dents varchar NOT NULL,'
                'commentaires varchar(200),'
                'FOREIGN KEY (rdv_id) REFERENCES rendezvous(rdv_id));')

cur.execute('CREATE TABLE procedures (procedure_id serial PRIMARY KEY,'
                'patient_id int NOT NULL,'
                'rdv_id int NOT NULL,'
                'date date NOT NULL,'
                'code_procedure varchar NOT NULL,'
                'type_procedure varchar NOT NULL,'
                'quantite_procedure int DEFAULT 1,'
                'FOREIGN KEY (rdv_id) REFERENCES rendezvous(rdv_id),'
                'FOREIGN KEY (patient_id) REFERENCES patients(patient_id));')

cur.execute('CREATE TABLE frais (frais_id serial PRIMARY KEY,'
                'procedure_id int NOT NULL,'
                'code_frais varchar NOT NULL,'
                'frais decimal(10,2) NOT NULL,'
                'FOREIGN KEY (procedure_id) REFERENCES procedures(procedure_id));')

cur.execute('CREATE TABLE assurance (reclamation_id serial PRIMARY KEY, '
                'patient_id int NOT NULL,'
                'paiement_id int NOT NULL,'
                'FOREIGN KEY (patient_id) REFERENCES patients(patient_id));')

cur.execute('CREATE TABLE utilisateurs (user_id serial PRIMARY KEY,'
                'username varchar NOT NULL UNIQUE,'
                'password varchar NOT NULL,'
                'patient_id int,'
                'employe_id int,'
                'is_patient boolean DEFAULT FALSE,'
                'is_receptionist boolean DEFAULT FALSE,'
                'is_dentist boolean DEFAULT FALSE,'
                'FOREIGN KEY (patient_id) REFERENCES patients(patient_id),'
                'FOREIGN KEY (employe_id) REFERENCES employes(employe_id));'
                )

cur.execute('INSERT INTO utilisateurs (username, password, employe_id, is_receptionist)'
                'VALUES (%s, %s, %s, %s)',
                ('testuser',
                'password',
                1,
                True)
                )

cur.execute('INSERT INTO utilisateurs (username, password, employe_id, is_dentist)'
                'VALUES (%s, %s, %s, %s)',
                ('testdentist',
                'password',
                2,
                True)
                )

cur.execute('INSERT INTO utilisateurs (username, password, patient_id, is_patient)'
                'VALUES (%s, %s, %s, %s)',
                ('johndoe',
                'password',
                1,
                True)
                )

conn.commit()

cur.close()
conn.close()

print("DB init complete.")