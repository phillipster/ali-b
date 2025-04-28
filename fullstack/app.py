from flask import Flask, request, jsonify, render_template, send_from_directory, \
    session, redirect, url_for
import mysql.connector

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = 'your_secret_key'  # VERY IMPORTANT: Set a secret key!

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
        query = "SELECT User, Password FROM mysql.user WHERE User = %s"
        print(f"Executing query: {query}, with username: {username}")
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        print(f"User found: {user}")
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
        query = f"SHOW GRANTS FOR '{username}'@'localhost'"
        print(f"Executing role query (SHOW GRANTS): {query}")
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"Grants found: {results}")

        for row in results:
            grant_statement = row[0]  # Each row is a grant statement
            if grant_statement.startswith("GRANT `"):
                # Extract the role name
                parts = grant_statement.split(" TO ")
                if len(parts) > 0:
                    role_part = parts[0]
                    role_name = role_part.split("`")[1]  # Get the role name within backticks
                    roles.append(role_name)
        print(f"Roles found (SHOW GRANTS): {roles}")
        return roles

    except mysql.connector.Error as err:
        print(f"Error getting user roles: {err}")
        return []
    finally:
        cursor.close()
        close_db_conn(conn)



def authenticate_user(username, password, selected_role):
    """
    Authenticates a user against MySQL's built-in password hashing.
    """
    print(f"Authenticating user: {username}, with password: {password}, and role: {selected_role}")
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Use MySQL's PASSWORD() function in the query.
        query = "SELECT User FROM mysql.user WHERE User = %s AND Password = PASSWORD(%s)"
        cursor.execute(query, (username, password))  # Pass plain-text password
        user = cursor.fetchone()

        if user:
            print("Password check passed (using MySQL PASSWORD() function)")
            user_roles = get_user_roles(username)
            print(f"User roles: {user_roles}")
            if selected_role in user_roles:
                print("Authentication successful")
                return True, user['User'], selected_role
            else:
                print("Role not found for user")
                return False, None, None
        else:
            print("Password check failed (using MySQL PASSWORD() function)")
            return False, None, None
    except mysql.connector.Error as err:
        print(f"Error during authentication: {err}")
        return False, None, None
    finally:
        cursor.close()
        close_db_conn(conn)



def create_new_user(username, password, role):
    """
    Creates a new user in the database.
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    try:
        create_user_sql = f"CREATE USER %s@'localhost' IDENTIFIED BY %s"
        cursor.execute(create_user_sql, (username, password))
        print('executed user creation')
        grant_role_sql = f"GRANT {role} TO %s@'localhost'"
        cursor.execute(grant_role_sql, (username,))
        print('role granted')
        conn.commit()
        return True, "User created successfully."

    except mysql.connector.Error as err:
        conn.rollback()
        error_message = f"Error creating user: {err}"
        print(error_message)
        return False, error_message
    finally:
        cursor.close()
        close_db_conn(conn)



@app.route('/create_user', methods=['GET', 'POST'])
def create_user_route():
    error = None
    success_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif role not in ['student', 'faculty']:
            error = "Invalid role.  Must be 'student' or 'faculty'."
        elif get_user_by_username(username):
            error = "Username already exists."

        if not error:
            success, message = create_new_user(username, password, role)
            if success:
                success_message = message
                return redirect(url_for('login'))
            else:
                error = message

    return render_template('create_user.html', error=error,
                           success_message=success_message)


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
            session['username'] = username # Store the username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username, password, or selected role'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    # Clear the session when the user logs out.
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in by checking for user_id in the session.
    if 'user_id' in session:
        user_id = session['user_id']
        role = session.get('role', 'Guest')
        username = session.get('username') # Get the username.
        return render_template('dashboard.html', user_id=user_id, role=role, username=username)  # Pass to template
    else:
        return redirect(url_for('login'))


@app.route("/")
def index():
    return send_from_directory('static', 'pages/index.html')


@app.route("/course_search")
def course_search():
    prof_name = request.args.get("prof_name", "").strip() or None
    min_cred = request.args.get("min_credits", type=int)
    max_cred = request.args.get("max_credits", type=int)
    degree_id = request.args.get("degree_id", type=int)

    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT degreeID, degree_name FROM degree")
    degrees = cur.fetchall()

    course_sql = """
      SELECT c.courseID, c.course_name, c.credits
      FROM courses c
    """
    course_args = []

    if degree_id:
        course_sql += " JOIN degree_requirements dr ON dr.courseID = c.courseID"
        course_sql += " WHERE dr.degreeID = %s"
        course_args.append(degree_id)

    if min_cred is not None:
        course_sql += " WHERE c.credits >= %s";
        course_args.append(min_cred)
    if max_cred is not None:
        course_sql += " WHERE c.credits <= %s";
        course_args.append(max_cred)

    course_sql += " ORDER BY c.course_name"
    cur.execute(course_sql, course_args)
    courses = cur.fetchall()

    sections = []
    print(prof_name)
    if prof_name:
        sec_sql = """
          SELECT DISTINCT 
            c.courseID, c.course_name, c.credits,
            p.prof_name
          FROM section s
          JOIN courses    c ON s.courseID    = c.courseID
          JOIN professor p ON s.professorID  = p.professorID
          WHERE p.prof_name LIKE %s
        """
        sec_args = [f"%{prof_name}%"]
        cur.execute(sec_sql, sec_args)
        sections = cur.fetchall()

    cur.close()
    conn.close()
    print("Sections: ", sections)

    return render_template(
        "course_search.html",
        degrees=degrees,
        filters=request.args,
        courses=courses,
        sections=sections
    )


@app.route("/page/<page>")
def load_page(page):
    if page == "schedule":
        return schedule_maker()
    if page == "professor":
        return render_template("professor.html")

    # otherwise render the plain template
    return render_template(f"{page}.html")


@app.route("/api/campus")
def api_items():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM campus WHERE campusID!=18")
    items = cursor.fetchall()
    cursor.close();
    conn.close()
    return jsonify(items)


@app.route("/api/schools")
def school_items():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM school")
    items = cursor.fetchall()
    cursor.close();
    conn.close()
    return jsonify(items)


@app.route("/api/degrees")
def degree_items():
    school_id = request.args.get('schoolID')
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM degree"
    if school_id:
        sql += " WHERE schoolID = %s"
        cursor.execute(sql, (school_id,))
    else:
        cursor.execute(sql)
    items = cursor.fetchall()
    cursor.close();
    conn.close()
    return jsonify(items)


@app.route("/api/professors")
def professor_items():
    department_id = request.args.get('departmentID')
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    sql = """
   SELECT p.professorID, p.prof_name, p.prof_email
   FROM professor p
  """
    args = []
    if department_id:
        sql += """
    JOIN professor_department pd ON p.professorID = pd.professorID
    WHERE pd.departmentID = %s
   """
        args.append(department_id)

    cursor.execute(sql, args)
    items = cursor.fetchall()
    cursor.close();
    conn.close()
    return jsonify(items)


@app.route("/api/departments")
def department_items():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT departmentID, department_name FROM department")
    items = cursor.fetchall()
    cursor.close();
    conn.close()
    return jsonify(items)


@app.route('/schedule')
def schedule_maker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    filters = {
        "p_department": request.args.get("p_department", ""),
        "p_courseID": request.args.get("p_courseID", ""),
        "p_course_name": request.args.get("p_course_name", ""),
        "p_description_includes": request.args.get(
            "p_description_includes", ""),
        "p_professor": request.args.get("p_professor", ""),
        "p_min_credits": request.args.get("p_min_credits", -1, type=int),
        "p_max_credits": request.args.get("p_max_credits", -1, type=int),
        "p_campus_available": request.args.get("p_campus_available", ""),
    }

    conn = get_db_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "CALL find_section(%(p_department)s, %(p_courseID)s, "
        "%(p_course_name)s, %(p_description_includes)s, "
        "%(p_professor)s, %(p_min_credits)s, %(p_max_credits)s, "
        "%(p_campus_available)s)",
        filters
    )
    sections = cur.fetchall()

    cur.execute("SELECT DISTINCT campus_name FROM campus")
    campuses = [r["campus_name"] for r in cur.fetchall()]

    cur.execute("""
      SELECT e.sectionID,
             s.courseID, c.course_name,
             ct.time_start, ct.time_end,
             pr.prof_name,
             ca.campus_name
      FROM enrollment e
      JOIN section       s  ON e.sectionID = s.sectionID
      JOIN courses       c  ON s.courseID  = c.courseID
      JOIN class_time    ct ON s.timeID     = ct.timeID
      JOIN professor     pr ON s.professorID= pr.professorID
      JOIN course_campus cc ON c.courseID   = cc.courseID
      JOIN campus        ca ON cc.campusID  = ca.campusID
      WHERE e.user_id = %s
      ORDER BY ct.time_start
    """, (user_id,))
    schedule = cur.fetchall()

    cur.close()
    close_db_conn(conn)

    return render_template(
        'schedule.html',
        sections=sections,
        campuses=campuses,
        schedule=schedule,
        filters=request.args
    )



@app.route('/enroll', methods=['POST'])
def enroll():
    user_id = session.get('user_id')
    section_id = request.json.get('sectionID')

    conn = get_db_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO enrollment (user_id, sectionID) VALUES (%s, %s)",
            (user_id, section_id)
        )
        conn.commit()
        return jsonify(success=True), 200

    except mysql.connector.Error as e:
        if e.sqlstate == '45000':
            return jsonify(success=False, error=e.msg), 409
        return jsonify(success=False, error="DB error"), 500

    finally:
        cur.close()
        close_db_conn(conn)


@app.route('/drop', methods=['POST'])
def drop():
    user_id = session.get('user_id')
    section_id = request.json.get('sectionID')
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM enrollment WHERE user_id=%s AND sectionID=%s",
        (user_id, section_id)
    )
    conn.commit()
    cur.close()
    close_db_conn(conn)
    return jsonify(success=True)


if __name__ == "__main__":
    app.run(debug=False)
