from flask import Flask, request, jsonify, render_template, send_from_directory
import mysql.connector


app = Flask(__name__, template_folder="templates", static_folder="static")

def get_db_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="albert"
    )

@app.route("/api/campus")
def api_items():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM campus")
    items = cursor.fetchall()
    cursor.close();
    conn.close()
    return jsonify(items)

@app.route("/")
def index():
    """Serve the static index.html file."""
    return send_from_directory('static', 'pages/index.html')
@app.route("/course_search")
def course_search():
    # ─── 1) Read filters or default to None ───────────────────────
    prof_name  = request.args.get("prof_name", "").strip() or None
    min_cred   = request.args.get("min_credits", type=int)
    max_cred   = request.args.get("max_credits", type=int)
    degree_req = request.args.get("degree_req")    # "yes", "no", or None

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



@app.route("/<page>")
def load_page(page):
    return render_template(f"{page}.html")

if __name__ == "__main__":
    app.run(debug=False)
