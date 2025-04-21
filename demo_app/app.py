from flask import Flask, jsonify, render_template
import mysql.connector

app = Flask(__name__, template_folder="templates")

def get_db_conn():
    return mysql.connector.connect(
      host="localhost",
      user="root",        # XAMPP default
      password="",        # XAMPP default
      database="albert"
    )

@app.route("/api/campus")
def api_items():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM campus")
    items = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(items)

@app.route("/")
def home():
    # serve our React‐powered page
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
