from flask import Flask, jsonify, render_template, send_from_directory, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = 'your_secret_key'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'albert'
}

def get_db_conn():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def close_db_conn(conn):
    if conn and conn.is_connected():
        conn.close()

def get_user_by_username(username):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    user = None
    try:
        # Assuming you have a 'role' column in your mysql.user table
        query = "SELECT User, Password, role FROM mysql.user WHERE User = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        close_db_conn(conn)
    return user

def get_user_roles(username):
    conn = get_db_conn()
    cursor = conn.cursor()
    roles = []
    try:
        # Query to get the active roles for the current user
        cursor.execute("SELECT CURRENT_ROLE()")
        current_role = cursor.fetchone()[0]
        if current_role:
            # If a specific role is active, return it
            roles.append(current_role)
        else:
            # If no specific role is active, get all granted roles
            cursor.execute("SELECT ROLE_NAME FROM INFORMATION_SCHEMA.APPLICABLE_ROLES WHERE GRANTEE = %s", (f"'username'@'localhost'",)) # Adjust username format if needed
            for row in cursor:
                roles.append(row[0])
    except mysql.connector.Error as err:
        print(f"Error getting user roles: {err}")
    finally:
        cursor.close()
        close_db_conn(conn)
    return roles

def authenticate_user(username, password, selected_role):
    user = get_user_by_username(username)
    if user and user['Password']:
        if check_password_hash(user['Password'], password):
            user_roles = get_user_roles(username)
            if selected_role in user_roles:
                return True, user['user_id'], selected_role
            else:
                return False, None, None
        else:
            return False, None, None
    return False, None, None
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        success, user_id, user_role = authenticate_user(username, password, role)
        if success:
            session['user_id'] = user_id
            session['role'] = user_role
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username, password, or selected role'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        role = session.get('role', 'Guest')
        return f"Welcome to the dashboard! Your user ID is {session['user_id']} and your role is: {role}"
    else:
        return redirect(url_for('login'))

@app.route("/")
def index():
    """Serve the static index.html file."""
    return send_from_directory('static', 'pages/index.html')

@app.route("/<page>")
def load_template(page):
    return render_template(f"{page}.html")

if __name__ == "__main__":
    app.run(debug=False)
# from flask import Flask, jsonify, render_template, send_from_directory
# import mysql.connector
#
# app = Flask(__name__, template_folder="templates", static_folder="static")
#
#
# def get_db_conn():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",
#         database="albert"
#     )
#
#
# @app.route("/")
# def index():
#     """Serve the static index.html file."""
#     return send_from_directory('static', 'pages/index.html')
#
#
# @app.route("/<page>")
# def load_template(page):
#     return render_template(f"{page}.html")
#
#
# if __name__ == "__main__":
#     app.run(debug=False)
