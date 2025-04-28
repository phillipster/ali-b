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
    conn = None
    cursor = None
    user = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT User, Password FROM mysql.user WHERE User = %s"
        print(f"Executing query: {query}, with username: {username}")
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        print(f"User found: {user}")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:  # Check if cursor exists before closing
            cursor.close()
        if conn:
            conn.close()
    return user


def get_user_roles(username):
    conn = None
    cursor = None
    roles = []
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def authenticate_user(username, password, selected_role):
    """
    Authenticates a user against MySQL's built-in password hashing.
    """
    print(f"Authenticating user: {username}, with password: {password}, and role: {selected_role}")
    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT User FROM mysql.user WHERE User = %s AND Password = PASSWORD(%s)"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            print("Password check passed (using MySQL PASSWORD() function)")
            user_roles = get_user_roles(username)
            print(f"User roles: {user_roles}")
            if selected_role in user_roles:
                if selected_role == 'faculty':
                    if instructor_passcode == "I<3Arfaoui":  # Check the passcode
                        print("Instructor passcode correct.")
                        return True, user['User'], selected_role
                    else:
                        print("Instructor passcode incorrect.")
                        return False, None, None
                else:  #  Student or other role
                    print("Role is not instructor, or instructor passcode check passed")
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def create_new_user(username, password, role):
    """
    Creates a new user in the database.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
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
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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
        instructor_passcode = request.form.get('instructor_passcode')  # Get passcode
        success, user_id, user_role = authenticate_user(username, password, role, instructor_passcode) # Pass it
        if success:
            session['user_id'] = user_id
            session['role'] = user_role
            session['username'] = username
            return redirect(url_for('schedule'))  # Redirect to schedule
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

    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cur = cursor
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

        return render_template(
            "course_search.html",
            degrees=degrees,
            filters=request.args,
            courses=courses,
        )
    except mysql.connector.Error as e:
        print(f"Error in course_search: {e}")
        return "An error occurred", 500  #  Return an error response
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/page/<page>")
def load_page(page):
    if page == "schedule":
        return schedule()
    return render_template(f"{page}.html")


@app.route("/api/campus")
def api_items():
    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM campus WHERE campusID!=18")
        items = cursor.fetchall()
        return jsonify(items)
    except mysql.connector.Error as e:
        print(f"Error in api_items: {e}")
        return jsonify(error="Database error"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/api/schools")
def school_items():
    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM school")
        items = cursor.fetchall()
        return jsonify(items)
    except mysql.connector.Error as e:
        print(f"Error in school_items: {e}")
        return jsonify(error="Database error"), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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


@app.route("/api/departments")
def department_items():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT departmentID, department_name FROM department")
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

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    username = session.get('username')

    conn = get_db_conn()  # Use the database connection from the context
    cursor = conn.cursor(dictionary=True)
    try:
        # 1) Read filters (defaults: "" or -1)
        vals = request.values  # covers both GET & POST
        dept = vals.get('p_department', "").strip()
        cid = vals.get('p_courseID', "").strip()
        cname = vals.get('p_course_name', "").strip()
        desc = vals.get('p_description_includes', "").strip()
        prof = vals.get('p_professor', "").strip()
        min_cr = int(vals.get('p_min_credits', -1) or -1)
        max_cr = int(vals.get('p_max_credits', -1) or -1)
        camp = vals.get('p_campus_available', "").strip()

        print("--- calling find_section with ---")
        print(dept, cid, cname, desc, prof, min_cr, max_cr, camp)

        # 2) Call the SP with exactly 8 arguments
        cursor.callproc(
            "find_section",
            (
                dept,
                cid,
                cname,
                desc,
                prof,
                min_cr,
                max_cr,
                camp,
            ),
        )

        # 3) Retrieve the rows your SP returned
        sections = []
        for result in cursor.stored_results():
            sections.extend(result.fetchall())
        print(f"sections → {len(sections)} rows")

        # 4) get campus list
        cursor.execute("SELECT DISTINCT campus_name FROM campus")
        campuses = [r["campus_name"] for r in cursor.fetchall()]

        # 5) one-param query for this user
        sql = """
              SELECT s.courseID,
                     c.course_name,
                     DATE_FORMAT(ct.time_start, '%%H:%%i:%%s') AS time_start,
                     DATE_FORMAT(ct.time_end, '%%H:%%i:%%s')   AS time_end,
                     pr.prof_name,
                     s.dates,
                     s.sectionID  /* Include sectionID in the query */
              FROM enrollment e
                       JOIN section s ON e.sectionID = s.sectionID
                       JOIN courses c ON s.courseID = c.courseID
                       JOIN class_time ct ON s.timeID = ct.timeID
                       JOIN professor pr ON s.professorID = pr.professorID
              WHERE e.username = %s
              ORDER BY ct.time_start
              """
        params = (user_id,)
        cursor.execute(sql, params)
        schedule1 = cursor.fetchall()

        # 6) render
        return render_template(
            "schedule.html",
            sections=sections,
            campuses=campuses,
            schedule=schedule1,
            filters={
                "p_department": dept,
                "p_courseID": cid,
                "p_course_name": cname,
                "p_description_includes": desc,
                "p_professor": prof,
                "p_min_credits": min_cr if min_cr != -1 else "",
                "p_max_credits": max_cr if max_cr != -1 else "",
                "p_campus_available": camp,
            },
            username=username,
        )

    except mysql.connector.Error as e:
        print("Error in schedule:", e)
        return "An internal error occurred", 500

    finally:
        cursor.close()
        # conn.close() # Removed:  The connection is now managed by the application context.




@app.route('/enroll', methods=['POST'])
def enroll():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    username = session.get('username')  # Get username from session
    section_id = request.json.get('sectionID')  # Get sectionID from the request

    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cur = cursor
        print(f"Attempting to enroll user {username} in section {section_id}")  # Debugging
        cur.execute(
            "INSERT INTO enrollment (username, sectionID) VALUES (%s, %s)",
            (username, section_id)  # Use username
        )
        conn.commit()
        print("Enrollment successful")
        #  Important:  Return the *updated* schedule data.
        sql = """
              SELECT s.courseID,
                     c.course_name,
                     DATE_FORMAT(ct.time_start, '%%H:%%i:%%s') AS time_start,
                     DATE_FORMAT(ct.time_end, '%%H:%%i:%%s')   AS time_end,
                     pr.prof_name,
                     s.dates,
                     s.sectionID
              FROM enrollment e
                       JOIN section s ON e.sectionID = s.sectionID
                       JOIN courses c ON s.courseID = c.courseID
                       JOIN class_time ct ON s.timeID = ct.timeID
                       JOIN professor pr ON s.professorID = pr.professorID
              WHERE e.username = %s  /* Changed to username */
              ORDER BY ct.time_start
              """
        params = (username,)  # Use username
        cursor.execute(sql, params)
        updated_schedule = cursor.fetchall()
        return jsonify(success=True, schedule=updated_schedule), 200  # Return updated schedule

    except mysql.connector.Error as e:
        conn.rollback()
        print(f"Error during enrollment: {e}")  # Log the full error
        if e.sqlstate == '45000':
            error_message = f"Enrollment failed: {e.msg}"
            print(error_message)
            return jsonify(success=False, error=error_message), 409
        error_message = f"Database error during enrollment: {e}"
        print(error_message)
        return jsonify(success=False, error=error_message), 500

    finally:
        if cursor:
            cursor.close()
        # if conn: #Removed, connections are handled by the application context.
        #     conn.close()
        pass



@app.route('/drop', methods=['POST'])
def drop():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    username = session.get('username')
    section_id = request.json.get('sectionID')  # Get sectionID from the request

    conn = None
    cursor = None
    try:
        conn = get_db_conn()  # Use the database connection from the application context
        cursor = conn.cursor()
        cur = cursor
        print(f"Attempting to drop user {username} from section {section_id}")  # Debugging
        cursor.execute(
            "DELETE FROM enrollment WHERE username=%s AND sectionID=%s",
            (username, section_id)  # Use username
        )
        conn.commit()
        print("Drop successful")

        # Return the updated schedule after successful drop
        sql = """
              SELECT s.courseID,
                     c.course_name,
                     DATE_FORMAT(ct.time_start, '%%H:%%i:%%s') AS time_start,
                     DATE_FORMAT(ct.time_end, '%%H:%%i:%%s')   AS time_end,
                     pr.prof_name,
                     s.dates,
                     s.sectionID
              FROM enrollment e
                       JOIN section s ON e.sectionID = s.sectionID
                       JOIN courses c ON s.courseID = c.courseID
                       JOIN class_time ct ON s.timeID = ct.timeID
                       JOIN professor pr ON s.professorID = pr.professorID
              WHERE e.username = %s /* Changed to username */
              ORDER BY ct.time_start
              """
        params = (username,) # Use username
        cursor.execute(sql, params)
        updated_schedule = cursor.fetchall()
        return jsonify(success=True, schedule=updated_schedule), 200  # Return the updated schedule

    except mysql.connector.Error as e:
        conn.rollback()
        print(f"Error dropping: {e}")
        error_message = f"Database error during drop: {e}"
        print(error_message)
        return jsonify(success=False, error=error_message), 500
    finally:
        if cursor:
            cursor.close()
        # if conn: #Removed, connections are handled by the application context.
        #     conn.close()
        pass

if __name__ == "__main__":
    app.run(debug=False)
