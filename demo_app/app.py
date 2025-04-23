from flask import Flask, jsonify, render_template, send_from_directory
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


@app.route("/campuses")
def campuses():
    return render_template("campuses.html")


if __name__ == "__main__":
    app.run(debug=False)
