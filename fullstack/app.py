from flask import Flask, request, jsonify, render_template, send_from_directory, \
    session, redirect, url_for
import mysql.connector
from werkzeug.security import check_password_hash

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
        query = "SELECT User, Password FROM mysql.user WHERE User = %s"
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
            cursor.execute(
                "SELECT ROLE_NAME FROM INFORMATION_SCHEMA.APPLICABLE_ROLES WHERE GRANTEE = %s",
                (f"'username'@'localhost'",))  # Adjust username format if needed
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
        success, user_id, user_role = authenticate_user(username, password,
                                                        role)
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


@app.route("/course_search")
def course_search():
    # ─── 1) Read filters or default to None ───────────────────────
    prof_name = request.args.get("prof_name", "").strip() or None
    min_cred = request.args.get("min_credits", type=int)
    max_cred = request.args.get("max_credits", type=int)
    degree_req = request.args.get("degree_req")  # "yes", "no", or None

    # ─── 2) Build base SQL + args list ────────────────────────────
    sql = """
    SELECT 
      c.courseID, c.course_name, c.credits,
      p.prof_name, dr.courseID AS is_degree_requirement

    FROM courses c
    JOIN section s      ON s.courseID    = c.courseID
    JOIN professor p    ON s.professorID  = p.professorID
    LEFT JOIN degree_requirements dr 
      ON dr.courseID   = c.courseID
    """
    args = []
    #lol
    # ─── 3) Append WHERE clauses for each filter ───────────────────
    if prof_name:
        sql += " AND p.prof_name LIKE %s"
        args.append(f"%{prof_name}%")
    if min_cred is not None:
        sql += " AND c.credits >= %s"
        args.append(min_cred)
    if max_cred is not None:
        sql += " AND c.credits <= %s"
        args.append(max_cred)
    if degree_req:
        # checkbox sends degree_req="on"
        sql += " AND dr.courseID IS NOT NULL"
    elif degree_req == "no":
        sql += " AND (dr.required = FALSE OR dr.required IS NULL)"

    # ─── 4) Final ordering ────────────────────────────────────────
    sql += " ORDER BY c.course_name"

    # ─── 5) Execute and fetch ─────────────────────────────────────
    conn = get_db_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute(sql, args)
    results = cur.fetchall()
    cur.close(); conn.close()

    # ─── 6) Render Jinja template, passing both filters & results ─
    return render_template(
      "course_search.html",
      filters=request.args,   # so the form stays populated
      results=results
    )


@app.route("/page/<page>")
def load_page(page):
    return render_template(f"{page}.html")


@app.route("/api/campus")
def api_items():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM campus")
    items = cursor.fetchall()
    cursor.close();
    conn.close()
    return jsonify(items)


if __name__ == "__main__":
    app.run(debug=False)
