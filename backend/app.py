from flask import Flask, request, jsonify
from flask_cors import CORS
import MySQLdb

app = Flask(__name__)
CORS(app)

app.config.update({
  'MYSQL_HOST':     'localhost',
  'MYSQL_USER':     'root',
  'MYSQL_PASSWORD': '',
  'MYSQL_DB':       'classreg'
})
db = MySQLdb.connect(
  host=app.config['MYSQL_HOST'],
  user=app.config['MYSQL_USER'],
  passwd=app.config['MYSQL_PASSWORD'],
  db=app.config['MYSQL_DB']
)

@app.route('/api/courses', methods=['GET'])
def list_courses():
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT courseID, course_name, credits FROM courses")
    return jsonify(cur.fetchall())

@app.route('/api/find_section', methods=['GET'])
def find_section():
    params = [request.args.get(p, '') for p in (
      'p_department','p_courseID','p_course_name','p_description_includes',
      'p_professor','p_min_credits','p_max_credits','p_campus_available')]
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.callproc('find_section', params)
    for result in cur.stored_results():
        rows = result.fetchall()
    return jsonify(rows)

@app.route('/api/enroll', methods=['POST'])
def enroll():
    data = request.json
    try:
        cur = db.cursor()
        cur.execute(
            "INSERT INTO enrollment (user_id, sectionID) VALUES (%s, %s)",
            (data['user_id'], data['sectionID'])
        )
        db.commit()
        return jsonify(status='ok'), 201
    except MySQLdb.Error as e:
        return jsonify(error=str(e)), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
