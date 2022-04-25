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

# Execute a command: this creates a new table
cur.execute('DROP TABLE IF EXISTS utilisateurs;')
cur.execute('CREATE TABLE utilisateurs (id serial PRIMARY KEY,'
                'username varchar (250) NOT NULL,'
                'password varchar (250) NOT NULL,'
                'role varchar(10) NOT NULL);'
                )

# Insert data into the table

cur.execute('INSERT INTO utilisateurs (username, password, role)'
                'VALUES (%s, %s, %s)',
                ('testuser',
                'password',
                'admin')
                )

conn.commit()

cur.close()
conn.close()

print("DB init complete.")