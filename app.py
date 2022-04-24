import os
import psycopg2
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object("config.Config")

def get_db_connection():
    conn = psycopg2.connect(
        host=app.config["DB_HOST"],
        port=app.config["DB_PORT"],
        database=app.config["DB_NAME"],
        user=app.config["DB_USERNAME"],
        password=app.config["DB_PASSWORD"])
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM books;')
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', books=books)

if __name__ == '__main__':
    app.run(port=7832, debug=True)