from curses import meta
from functools import wraps
from numpy import require
import psycopg2.extras
from flask import Flask, flash, redirect, render_template, url_for, abort, request, g

app = Flask(__name__)
app.secret_key = "secretKey"
app.config.from_object("config.Config")

loggedInUser = None

# TODO: Catch exceptions on all pyscopg2 database calls

# Needed role for access can be specified with user_type
def login_required(user_type = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not loggedInUser:
                return redirect(url_for('login'))
            elif user_type:
                if user_type == 'patient' and not loggedInUser['is_patient']:
                    return abort(403)
                elif user_type == 'dentist' and not loggedInUser['is_dentist']:
                    return abort(403)
                elif user_type == 'receptionist' and not loggedInUser['is_receptionist']:
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

def refetch_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM utilisateurs WHERE user_id={};".format(user_id))
    return cur.fetchone()

def search_patient_by_name(name_query):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT patient_id, nom FROM patients WHERE UPPER(nom) LIKE '%{}%';".format(name_query.upper()))
    found_patients = cur.fetchall()
    #print(found_patients, flush=True)
    cur.close()
    return found_patients

def add_procedure(procedureCode, rdv_id, patient_id, date):
    type_procedure = ""
    if procedureCode == 1:
        type_procedure = "Blanchissement"
    elif procedureCode == 2:
        type_procedure = "Plombage"
    elif procedureCode == 3:
        type_procedure = "Broches"
    else:
        procedureCode = 0
        type_procedure = "Nettoyage"
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO procedures (rdv_id, patient_id, code_procedure, type_procedure, date)"
                    "VALUES (%s, %s, %s, %s, %s) RETURNING procedure_id",
                    (rdv_id,
                    patient_id,
                    procedureCode,
                    type_procedure,
                    date))
    returned_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return returned_id
    

@app.route('/')
@login_required()
def index():
    #conn = get_db_connection()
    #cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # Fetch data as dictionnary instead of list
    #cur.execute('SELECT * FROM utilisateurs;') # Just a test query
    #users = cur.fetchall()
    #cur.close()
    if loggedInUser['is_receptionist']:
        return redirect(url_for('receptionist_index'))
    elif loggedInUser['is_dentist']:
        return redirect(url_for('dentist_index'))
    else:
        return redirect(url_for('patient_index'))

@app.route('/patient/setid', methods=['GET', 'POST'])
@login_required()
def patient_set_id():
    global loggedInUser
    if request.method == 'POST':
        
        entered_patient_id = request.form['patientId']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM patients WHERE patient_id={}'.format(entered_patient_id))
        if not cur.fetchone() is None:
            cur.execute('UPDATE utilisateurs SET patient_id={}, is_patient=TRUE WHERE user_id={}'.format(entered_patient_id, loggedInUser['user_id']))
            conn.commit()
            cur.close()
            loggedInUser = refetch_user(loggedInUser['user_id'])
            return redirect(url_for('patient_index'))
        else:
            flash("Ce ID de patient n'existe pas, vérifiez qu'il soit bien entré")
    
    return render_template('patient/set_id.html', loggedInUser=loggedInUser)

@app.route('/patient')
@login_required()
def patient_index():
    if not loggedInUser['is_patient']:
        return redirect(url_for('patient_set_id'))
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM rendezvous WHERE patient_id={} AND date_rdv > now() ORDER BY date_rdv ASC;'.format(loggedInUser['patient_id']))
    appointments = cur.fetchall()
    cur.execute('SELECT * FROM procedures WHERE patient_id={} AND date < now() ORDER BY date DESC;'.format(loggedInUser['patient_id']))
    antecedents = cur.fetchall()
    cur.execute("SELECT * FROM employes WHERE type_employe='dentist';")
    dentists = cur.fetchall()
    cur.execute("SELECT * FROM succursales;")
    succursales = cur.fetchall()
    cur.close()
    
    return render_template('patient/index.html', loggedInUser=loggedInUser, appointments=appointments, antecedents=antecedents, dentistes=dentists, succursales=succursales)

@app.route('/receptionist')
@login_required(user_type='receptionist')
def receptionist_index():
    return render_template('receptionist/index.html', loggedInUser=loggedInUser)

@app.route('/dentist')
@login_required(user_type='dentist')
def dentist_index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM rendezvous WHERE dentist_id={} AND date_rdv >= now() ORDER BY date_rdv ASC;'.format(loggedInUser['employe_id']))
    appointments = cur.fetchall()
    cur.execute('SELECT patient_id, nom FROM patients;')
    patients = cur.fetchall()
    cur.close()
    return render_template('dentist/index.html', loggedInUser=loggedInUser, appointments=appointments, patients=patients)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # Fetch data as dictionnary instead of list
        cur.execute("SELECT * FROM utilisateurs WHERE UPPER(username)='{}' AND password='{}';".format(username.upper(), password))
        fetched_user = cur.fetchone()
        cur.close()
        
        if fetched_user:
            global loggedInUser
            loggedInUser = fetched_user
            return redirect(url_for('index'))
        else:
            flash("L'utilisateur n'a pas été trouvé. Assurez-vous d'avoir bien entré les détails de connection.")
    
    return render_template('login.html')

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passwordConfirm = request.form['passwordConfirm']
        
        if not password == passwordConfirm:
            flash("Les mots de passes entrés ne correspondent pas")
        else:  
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM utilisateurs WHERE UPPER(username)='{}'".format(username.upper()))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO utilisateurs (username, password)"
                        "VALUES (%s, %s)",
                        (username,
                        password))
                conn.commit()
                return redirect(url_for('login'))
            else:
                flash("Le nom d'utilisateur est déjà utilisé")
                
            cur.close()
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    global loggedInUser
    loggedInUser = None
    return redirect(url_for('login'))

### Patient

@app.route('/patient/succursales')
def show_succursales():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM succursales')
    fetched_succursales = cur.fetchall()
    cur.close()
    return render_template('patient/succursales.html', loggedInUser=loggedInUser, succursales=fetched_succursales)

@app.route('/patient/succursales/<int:succursale_id>')
def get_succursale_details(succursale_id):
    succursale_name = request.args.get('succursale_name')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT nom, role FROM employes WHERE succursale_id={} AND type_employe='dentist'".format(succursale_id))
    fetched_dentistes = cur.fetchall()
    cur.close()
    return render_template('patient/succursale_details.html', loggedInUser=loggedInUser, succursale_name=succursale_name, dentistes=fetched_dentistes)

### Receptionist
@app.route('/receptionist/patient/add', methods=['GET', 'POST'])
@login_required(user_type='receptionist')
def receptionist_patient_add():
    # TODO: Add some field validation
    if request.method == 'POST':
        new_name = request.form['patientName']
        new_sex = request.form['patientSex']
        new_SSN = request.form['patientSSN']
        new_email = request.form['patientEmail']
        new_DOB = request.form['patientDOB']
        new_phone = request.form['patientPhone']
        new_address = request.form['patientAddress']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO patients (nom, sexe, SSN, email, date_naissance, telephone, addresse)"
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING patient_id",
                    (new_name,
                    new_sex,
                    new_SSN,
                    new_email,
                    new_DOB,
                    new_phone,
                    new_address))
        returned_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return redirect(url_for('receptionist_modify_patient', patient_id = returned_id))
    
    return render_template('receptionist/patient_add.html', loggedInUser=loggedInUser)

@app.route('/receptionist/employee/add', methods=['GET', 'POST'])
@login_required(user_type='receptionist')
def receptionist_employee_add():
    # TODO: Add some field validation
    if request.method == 'POST':
        new_name = request.form['employeName']
        new_address = request.form['employeAddress']
        new_SSN = request.form['employeSSN']
        new_salary = request.form['employeSalary']
        form_employe_type = request.form['employeType']
        employe_username = request.form['employeUsername']
        
        new_employe_type = ""
        new_role = ""
        sql_role = ""
        if form_employe_type == "receptionist":
            new_employe_type = "receptionist"
            new_role = "Réceptionniste"
            sql_role = "is_receptionist=TRUE"
        elif form_employe_type == "hygienist":
            new_employe_type = "dentist"
            new_role = "Hygiéniste"
            sql_role = "is_dentist=TRUE"
        elif form_employe_type == "dentist":
            new_employe_type = "dentist"
            new_role = "Dentiste"
            sql_role = "is_dentist=TRUE"
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT succursale_id FROM employes WHERE employe_id={};'.format(loggedInUser['employe_id']))
        succursale_id = cur.fetchone()[0]
        cur.execute('INSERT INTO employes (succursale_id, nom, adresse, role, type_employe, SSN, salaire)'
                'VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING employe_id',
                (succursale_id,
                new_name,
                new_address,
                new_role,
                new_employe_type,
                new_SSN,
                new_salary))
        returned_id = cur.fetchone()[0]
        cur.execute("UPDATE utilisateurs SET employe_id={}, {} WHERE username='{}'".format(returned_id, sql_role, employe_username))
        conn.commit()
        cur.close()
        return redirect(url_for('receptionist_index'))
    
    return render_template('receptionist/employe_add.html', loggedInUser=loggedInUser)

@app.route('/receptionist/patient/search', methods=['GET', 'POST'])
@login_required(user_type='receptionist')
def receptionist_patient_search():
    found_patients = None
    
    if request.method == 'POST':
        name_query = request.form['q']
        if name_query is None: name_query = ""
        
        found_patients = search_patient_by_name(name_query)
        
    return render_template('receptionist/search.html', loggedInUser=loggedInUser, results = found_patients)

@app.route('/receptionist/patient/details/<int:patient_id>', methods=['GET', 'POST'])
@login_required(user_type='receptionist')
def receptionist_modify_patient(patient_id):
    # TODO: Add some field validation
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # Fetch data as dictionnary instead of list
    
    if request.method == 'POST':
        new_name = request.form['patientName']
        new_sex = request.form['patientSex']
        new_SSN = request.form['patientSSN']
        new_email = request.form['patientEmail']
        new_DOB = request.form['patientDOB']
        new_phone = request.form['patientPhone']
        new_address = request.form['patientAddress']
        cur.execute("UPDATE patients SET nom='" + new_name + "',"
                    "sexe='" + new_sex + "',"
                    "SSN=" + new_SSN + ","
                    "email='" + new_email + "',"
                    "date_naissance='" + new_DOB + "',"
                    "telephone=" + new_phone + ","
                    "addresse='" + new_address + "'"
                    "WHERE patient_id={};".format(patient_id))
        conn.commit()
        flash('Patient mis à jour')
    
    cur.execute("SELECT * FROM patients WHERE patient_id={};".format(patient_id))
    fetched_patient = cur.fetchone()
    cur.execute('SELECT * FROM rendezvous WHERE patient_id={} AND date_rdv > now() ORDER BY date_rdv DESC;'.format(fetched_patient['patient_id']))
    appointments = cur.fetchall()
    cur.close()
    
    return render_template('receptionist/patient_details.html', loggedInUser=loggedInUser, patient=fetched_patient, appointments=appointments)

@app.route('/receptionist/patient/book/<int:patient_id>', methods=['GET', 'POST'])
@login_required(user_type='receptionist')
def receptionist_book_appointment(patient_id):
    # TODO: Add some field validation
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT succursale_id FROM employes WHERE employe_id={};'.format(loggedInUser['employe_id']))
    currEmploye = cur.fetchone()
    appointment_succursale = int(currEmploye['succursale_id'])
    
    if request.method == 'POST':
        appointment_dentist = int(request.form['appointmentDentist'])
        appointment_date = request.form['appointmentDate']
        appointment_time = request.form['appointmentTime']
        appointment_procedures = request.form.getlist('appointmentProcedures')
        
        cur.execute('INSERT INTO rendezvous (patient_id, dentist_id, succursale_id, date_rdv, qty_procedure)'
                'VALUES (%s, %s, %s, %s, %s) RETURNING rdv_id',
                (patient_id,
                appointment_dentist,
                appointment_succursale,
                "{} {}:00".format(appointment_date, appointment_time),
                len(appointment_procedures)))
        returned_id = cur.fetchone()['rdv_id']
        conn.commit()
        print("Returned id: {}".format(returned_id), flush=True)
        
        for procedure in appointment_procedures:
            add_procedure(procedure, returned_id, patient_id, appointment_date)
            print("Added procedure {}".format(procedure), flush=True)
        
        return redirect(url_for('receptionist_modify_patient', patient_id=patient_id))
    
    cur.execute("SELECT * FROM employes WHERE type_employe='{}';".format('dentist'))
    fetched_dentists = cur.fetchall()
    if fetched_dentists is None:
        fetched_dentists = []
        
    cur.execute("SELECT * FROM succursales WHERE succursale_id={};".format(appointment_succursale))
    fetched_succursale = cur.fetchone()
    if fetched_succursale is None:
        fetched_succursale = ""
        
    cur.close()
    
    return render_template('receptionist/book_appointment.html', loggedInUser=loggedInUser, dentistes=fetched_dentists, succursale=fetched_succursale)

### Dentist
@app.route('/dentist/patient/search', methods=['GET', 'POST'])
@login_required(user_type='dentist')
def dentist_patient_search():
    found_patients = None
    
    if request.method == 'POST':
        name_query = request.form['q']
        if name_query is None: name_query = ""
        
        found_patients = search_patient_by_name(name_query)
        
    return render_template('dentist/search.html', loggedInUser=loggedInUser, results = found_patients)

@app.route('/dentist/patient/details/<int:patient_id>')
@login_required(user_type='dentist')
def dentist_patient_details(patient_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) # Fetch data as dictionnary instead of list
    cur.execute("SELECT * FROM patients WHERE patient_id={};".format(patient_id))
    fetched_patient = cur.fetchone()
    cur.execute('SELECT * FROM procedures WHERE patient_id={} AND date < now() ORDER BY date DESC;'.format(fetched_patient['patient_id']))
    antecedents = cur.fetchall()
    cur.close()
    
    return render_template('dentist/patient_details.html', loggedInUser=loggedInUser, patient=fetched_patient, antecedents=antecedents)

if __name__ == '__main__':
    app.run(port=7832, debug=True)