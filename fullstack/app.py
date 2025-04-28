from flask import Flask, request, jsonify, render_template, send_from_directory, \
    session, redirect, url_for
import mysql.connector
import datetime

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
        print("Database connection established")
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def close_db_conn(conn):
    if conn and conn.is_connected():
        conn.close()
        print("Database connection closed")

#
def get_user_by_username(username):
    conn = None
    cursor = None
    user = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT User, Password FROM mysql.user WHERE User = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_db_conn(conn)
    return user


def get_user_roles(username):
    conn = None
    cursor = None
    roles = []
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        query = f"SHOW GRANTS FOR '{username}'@'localhost'"
        cursor.execute(query)
        results = cursor.fetchall()
        for row in results:
            grant_statement = row[0]
            if grant_statement.startswith("GRANT `"):
                parts = grant_statement.split(" TO ")
                if len(parts) > 0:
                    role_part = parts[0]
                    role_name = role_part.split("`")[1]
                    roles.append(role_name)
        return roles
    except mysql.connector.Error as err:
        print(f"Error getting user roles: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_db_conn(conn)


def authenticate_user(username, password, selected_role, instructor_passcode=None):
    """
    Authenticates a user based on username, password, selected role,
    and an optional instructor passcode.
    """
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT User FROM mysql.user WHERE User = %s AND Password = PASSWORD(%s)"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            user_roles = get_user_roles(username)
            if selected_role in user_roles:
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()
                actual_user_id = user_data['user_id'] if user_data else None

                if selected_role == 'faculty':
                    if instructor_passcode == "12345":
                        return True, actual_user_id, selected_role
                    else:
                        return False, None, None
                else:
                    return True, actual_user_id, selected_role
            else:
                return False, None, None
        else:
            return False, None, None
    except mysql.connector.Error as err:
        print(f"Error during authentication: {err}")
        return False, None, None
    finally:
        if cursor:
            cursor.close()
        if conn:
            close_db_conn(conn)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        instructor_passcode = request.form.get('instructor_passcode')
        success, actual_user_id, user_role = authenticate_user(username, password, role, instructor_passcode)
        if success:
            print(f"[DEBUG - /login] Successful login. User ID: {actual_user_id}")
            session['user_id'] = actual_user_id
            session['role'] = user_role
            session['username'] = username
            return redirect(url_for('schedule'))
        else:
            error = 'Invalid username, password, or selected role'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # Clear the session when the user logs out.
    session.clear()
    return redirect(url_for('login'))

def create_new_user(username, password, role):
    """
    Creates a new user in the MySQL user table and your application's users table.
    Assumes 'users' table has auto-incrementing 'user_id' and 'username'.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_conn()
        cursor = conn.cursor()

        # 1. Create the user in MySQL user management
        create_user_sql = f"CREATE USER %s@'localhost' IDENTIFIED BY %s"
        cursor.execute(create_user_sql, (username, password))
        print('executed MySQL user creation')

        # 2. Grant the specified role
        grant_role_sql = f"GRANT {role} TO %s@'localhost'"
        cursor.execute(grant_role_sql, (username,))
        print('role granted')

        # 3. Insert the user into your 'users' table (user_id will auto-increment)
        insert_user_sql = "INSERT INTO users (username) VALUES (%s)"
        cursor.execute(insert_user_sql, (username,))
        print('inserted user into users table')

        conn.commit()
        return True, "User created successfully."

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        error_message = f"Error creating user: {err}"
        print(error_message)
        return False, error_message
    finally:
        if cursor:
            cursor.close()
        if conn:
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
        # elif role == 'faculty' :
        #     instructor_creation_passcode = request.form.get('instructor_passcode')
        #     if instructor_creation_passcode != "12345":
        #         error = "Incorrect instructor creation passcode."

        if not error:
            success, message = create_new_user(username, password, role)
            if success:
                success_message = message
                return redirect(url_for('login'))
            else:
                error = message

    return render_template('create_user.html', error=error,
                           success_message=success_message)

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

    where_conditions = []
    if degree_id:
        course_sql += " JOIN degree_requirements dr ON dr.courseID = c.courseID"
        where_conditions.append("dr.degreeID = %s")
        course_args.append(degree_id)

    if min_cred is not None:
        where_conditions.append("c.credits >= %s")
        course_args.append(min_cred)
    if max_cred is not None:
        where_conditions.append("c.credits <= %s")
        course_args.append(max_cred)

    if where_conditions:
        course_sql += " WHERE " + " AND ".join(where_conditions)

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
    
    try:
        cursor.execute(sql, args)
        items = cursor.fetchall()
        return jsonify(items)
    except mysql.connector.Error as e:
        print(f"Error in professor_items: {e}")
        return jsonify(error="Database error"), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    username = session.get('username')

    print(f"[DEBUG] User ID from session in /schedule: {user_id}")

    conn = get_db_conn()
    if conn is None:
        return "Database connection error", 500
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

        # 2) Call the SP to get available sections
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

        # 3) Retrieve available sections
        sections = []
        for result in cursor.stored_results():
            sections_data = result.fetchall()
            print(f"Sections data from stored procedure: {sections_data}")
            for row in sections_data:
                sections.append({
                    'sectionID': row.get('sectionID'),
                    'department_name': row.get('department_name'),
                    'school_name': row.get('school_name'),
                    'instructor_name': row.get('instructor_name'),
                    'instructor_email': row.get('instructor_email'),
                    'campus_name': row.get('campus_name'),
                    'campus_address': row.get('campus_address'),
                    'time_start': row.get('time_start'),
                    'time_end': row.get('time_end'),
                    'courseID': row.get('courseID'),
                    'course_name': row.get('course_name'),
                    'course_description': row.get('course_description'),
                    'credits': row.get('credits'),
                    'prerequisite': row.get('prerequisite'),
                    'dates': row.get('dates'),
                    'section_name': row.get('section_name'),
                    'class_times': get_class_times_for_section(cursor, row.get('timeID'))  # Get class times
                })
        print(f"Sections data being passed to template: {sections}")
        print(f"[DEBUG] section built: {sections}")  # <-- Add this line
        # 4) get campus list
        cursor.execute("SELECT DISTINCT campus_name FROM campus")
        campuses = [r["campus_name"] for r in cursor.fetchall()]
        print(f"Campuses: {campuses}") #debug

        # 5) Fetch enrolled sections
        sql = """
              SELECT s.sectionID, \
                     s.timeID,
                     c.courseID,
                     c.course_name,
                     pr.prof_name
              FROM enrollment e
                       JOIN section s ON e.section_id = s.sectionID
                       JOIN courses c ON s.courseID = c.courseID
                       JOIN professor pr ON s.professorID = pr.professorID
              WHERE e.user_id = %s
              """
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        print(f"[DEBUG] Raw enrolled rows: {rows}")  # Add this line

        # 6) Massage enrolled sections into a list of dicts and extract IDs
        schedule1 = []
        enrolled_section_ids = []
        for r in rows:
            time_data = get_class_times_for_section(cursor, r.get('timeID'))
            class_times = []
            if time_data:
                class_times.append(time_data)

            schedule1_row = {
                'sectionID': r['sectionID'],
                'courseID': r['courseID'],
                'course_name': r['course_name'],
                'prof_name': r['prof_name'],
                'class_times': class_times
            }
            schedule1.append(schedule1_row)
            enrolled_section_ids.append(r['sectionID'])  # Add the sectionID to the list
            print(f"[DEBUG] Enrolled section built: {schedule1_row}")  # Debug for each enrolled section
        print(f"[DEBUG] Enrolled Section IDs: {enrolled_section_ids}")  # Debug for the entire list
        # 7) render
        print(f"[DEBUG] Schedule data being passed to template: {schedule1}")
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
            enrolled_section_ids=enrolled_section_ids,
        )

    except mysql.connector.Error as e:
        print("Error in schedule:", e)
        return "An internal error occurred", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_class_times_for_section(cursor, time_id):
    sql = """
        SELECT
            time_start,
            time_end,
            monday,
            tuesday,
            wednesday,
            thursday,
            friday,
            saturday,
            sunday
        FROM class_time
        WHERE timeID = %s
    """
    cursor.execute(sql, (time_id,))
    row = cursor.fetchone()
    if not row:
        return {}

    # 🆕 Convert timedelta to readable "HH:MM" string
    def format_timedelta(td):
        if isinstance(td, datetime.timedelta):
            total_seconds = int(td.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        return str(td)  # fallback

    time_start_str = format_timedelta(row['time_start'])
    time_end_str = format_timedelta(row['time_end'])

    # Build a list of weekday names that are marked true
    days = []
    for day in ('monday','tuesday','wednesday','thursday','friday','saturday','sunday'):
        if row.get(day):
            days.append(day.capitalize())

    return {
        'time_start': time_start_str,
        'time_end': time_end_str,
        'days': days
    }

@app.route('/update_course_credits', methods=['POST'])
def update_course_credits():
    if 'user_id' not in session or session.get('role') != 'faculty':
        return jsonify(success=False, error="Unauthorized"), 403

    course_id = request.form.get('courseID')
    new_credits = request.form.get('credits', type=int)

    if not course_id or new_credits is None:
        return jsonify(success=False, error="Missing courseID or credits"), 400

    conn = get_db_conn()
    if not conn:
        return jsonify(success=False, error="Database connection failed"), 500

    cursor = conn.cursor()
    try:
        update_query = "UPDATE courses SET credits = %s WHERE courseID = %s"
        cursor.execute(update_query, (new_credits, course_id))
        conn.commit()
        return jsonify(success=True, message=f"Course {course_id} credits updated to {new_credits}")
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify(success=False, error=f"Database error: {err}"), 500
    finally:
        if cursor:
            cursor.close()
        close_db_conn(conn)

        
@app.route('/get_enrolled_sections')
def get_enrolled_sections():
    if 'user_id' not in session:
        return jsonify(success=False), 403
    user_id = session['user_id']
    print("USEDID: ", user_id)
    conn = get_db_conn()
    if not conn:
        return jsonify(success=False), 500
    cursor = conn.cursor(dictionary=True)
    sql = """
          SELECT s.sectionID,
                 s.timeID,
                 c.courseID,
                 c.course_name,
                 pr.prof_name
          FROM enrollment e
                   JOIN section s ON e.section_id = s.sectionID
                   JOIN courses c ON s.courseID = c.courseID
                   JOIN professor pr ON s.professorID = pr.professorID
          WHERE e.user_id = %s
          """
    cursor.execute(sql, (user_id,))
    enrolled = cursor.fetchall()

    for section in enrolled:
        class_time = get_class_times_for_section(cursor, section['timeID'])
        section['class_times'] = [class_time] if class_time else []
        section.pop('timeID', None)

    cursor.close()
    return jsonify(success=True, schedule=enrolled)


@app.route('/enroll', methods=['POST'])
def enroll():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    username = session.get('username')
    section_id = request.json.get('sectionID')

    conn = get_db_conn()
    if conn is None:
        return jsonify(success=False, error="Failed to connect to the database"), 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        print(f"Attempting to enroll user {username} in section {section_id}")

        # 1. Validate section exists
        cursor.execute("SELECT sectionID FROM section WHERE sectionID = %s", (section_id,))
        section_exists = cursor.fetchone()
        if not section_exists:
            return jsonify(success=False, error=f"Section with ID '{section_id}' does not exist."), 400

        # 2. Get user_id
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        user_row = cursor.fetchone()
        if user_row is None:
            return jsonify(success=False, error=f"User with username '{username}' not found."), 400
        actual_user_id = user_row['user_id']
        print(f"Actual user ID from database: {actual_user_id}")

        # 3. Insert into enrollment
        cursor.execute(
            "INSERT INTO enrollment (user_id, section_id) VALUES (%s, %s)",
            (actual_user_id, section_id),
        )
        conn.commit()
        print("Enrollment successful")

        # 4. Fetch updated schedule (including timeID)
        sql = """
              SELECT s.sectionID,
                     s.timeID,
                     c.courseID,
                     c.course_name,
                     pr.prof_name
              FROM enrollment e
                       JOIN section s ON e.section_id = s.sectionID
                       JOIN courses c ON s.courseID = c.courseID
                       JOIN professor pr ON s.professorID = pr.professorID
              WHERE e.user_id = %s
              """
        params = (actual_user_id,)
        cursor.execute(sql, params)
        updated_schedule = cursor.fetchall()

        # 5. Attach class_times for each section
        for section in updated_schedule:
            class_time = get_class_times_for_section(cursor, section['timeID'])
            section['class_times'] = [class_time] if class_time else []
            section.pop('timeID', None)  # 🔥 remove timeID before sending back

        print(f"Updated schedule after enrollment: {updated_schedule}")
        return jsonify(success=True, schedule=updated_schedule), 200

    except mysql.connector.Error as e:
        conn.rollback()
        print(f"Error during enrollment: {e}")
        if e.errno == 1062:
            return jsonify(success=False, error="You are already enrolled in this section."), 409
        elif e.errno == 1452:
            return jsonify(success=False, error="The section ID you provided does not exist, or the user does not exist."), 400
        else:
            return jsonify(success=False, error=f"Database error during enrollment: {e}"), 500

    finally:
        if cursor:
            cursor.close()


@app.route('/drop', methods=['POST'])
def drop():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    username = session.get('username')
    section_id = request.json.get('sectionID')

    conn = get_db_conn()
    if conn is None:
        return jsonify(success=False, error="Failed to connect to the database"), 500
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        print(f"Attempting to drop user {username} from section {section_id}")

        # 1. Delete enrollment
        cursor.execute(
            "DELETE FROM enrollment WHERE user_id=%s AND section_id=%s",
            (user_id, section_id)
        )
        conn.commit()
        print("Drop successful")

        # 2. Query remaining enrolled sections (including timeID!!)
        sql = """
              SELECT s.sectionID,
                     s.timeID,
                     c.courseID,
                     c.course_name,
                     pr.prof_name
              FROM enrollment e
                       JOIN section s ON e.section_id = s.sectionID
                       JOIN courses c ON s.courseID = c.courseID
                       JOIN professor pr ON s.professorID = pr.professorID
              WHERE e.user_id = %s
              """
        params = (user_id,)
        cursor.execute(sql, params)
        updated_schedule = cursor.fetchall()

        # 3. Add class_times to each
        for section in updated_schedule:
            class_time = get_class_times_for_section(cursor, section['timeID'])
            section['class_times'] = [class_time] if class_time else []
        print(f"Updated schedule after drop: {updated_schedule}")

        return jsonify(success=True, schedule=updated_schedule), 200

    except mysql.connector.Error as e:
        conn.rollback()
        print(f"Error dropping: {e}")
        error_message = f"Database error during drop: {e}"
        return jsonify(success=False, error=error_message), 500
    finally:
        if cursor:
            cursor.close()


if __name__ == "__main__":
    app.run(debug=False)