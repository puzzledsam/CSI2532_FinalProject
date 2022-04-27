from functools import wraps
import psycopg2.extras
from flask import Flask, flash, redirect, render_template, url_for, abort, request, g

app = Flask(__name__)
app.secret_key = "secretKey"
app.config.from_object("config.Config")

loggedInUser = None

# Needed role for access can be specified with user_type
def login_required(user_type = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not loggedInUser:
                return redirect(url_for('login'))
            elif user_type and not loggedInUser['type_utilisateur'] == user_type:
                return abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = psycopg2.connect(
            host=app.config["DB_HOST"],
            port=app.config["DB_PORT"],
            database=app.config["DB_NAME"],
            user=app.config["DB_USERNAME"],
            password=app.config["DB_PASSWORD"])
        
    return g.db_conn

# Automatically manage the database connection, as necessary
@app.teardown_appcontext
def teardown_db(exception):
    db_conn = g.pop('db_conn', None)
    
    if db_conn is not None:
        db_conn.close()

@app.route('/')
@login_required()
def index():
    # TODO: Redirect to proper user location based on role
    #conn = get_db_connection()
    #cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # Fetch data as dictionnary instead of list
    #cur.execute('SELECT * FROM utilisateurs;') # Just a test query
    #users = cur.fetchall()
    #cur.close()
    if loggedInUser['type_utilisateur'] == 'receptionist':
        return render_template('receptionist/index.html')
    else:
        return abort(404)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # Fetch data as dictionnary instead of list
        cur.execute("SELECT * FROM utilisateurs WHERE username='{}' AND password='{}';".format(username, password))
        fetched_user = cur.fetchone()
        cur.close()
        
        if fetched_user:
            global loggedInUser
            loggedInUser = fetched_user
            return redirect(url_for('index'))
        else:
            flash("L'utilisateur n'a pas été trouvé. Assurez-vous d'avoir bien entré les détails de connection.")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    global loggedInUser
    loggedInUser = None
    return redirect(url_for('login'))

# Receptionist
@app.route('/patient/search', methods=['GET', 'POST'])
@login_required()
def patient_search():
    found_patients = None
    
    if request.method == 'POST':
        name_query = request.form['q']
        if name_query is None: name_query = ""
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT patient_id, nom FROM patients WHERE UPPER(nom) LIKE '%" + name_query.upper() + "%'")
        found_patients = cur.fetchall()
        print(found_patients, flush=True)
        cur.close()
    
    return render_template('receptionist/search.html', results = found_patients)

if __name__ == '__main__':
    app.run(port=7832, debug=True)