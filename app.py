import sqlite3
import os

from flask import Flask, flash, escape, request, jsonify, json, g, redirect, url_for, send_from_directory


DATABASE = './database.db'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'json'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('./schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Skip the following line if this is not the first time running app.py.
init_db()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=(), one=False):
    db = get_db()
    cursor = db.cursor()
    count = cursor.execute(query, args)
    db.commit()
    cursor.close()
    return count

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

random_number = 1

@app.route('/api/tests', methods = ['POST'])
def math():
	global random_number
	content = request.get_json()

	test_id = random_number
	subject_from_json = content["subject"]
	answer_keys_from_json = json.dumps(content["answer_keys"])
	answer_keys_from_json = answer_keys_from_json.replace('"', '\'')

	insert_query = "INSERT INTO exam (test_id, subject, answer_keys) VALUES (\"" + str(test_id) + "\", \"" + subject_from_json + "\", \"" + answer_keys_from_json + "\")"

	insert_db(insert_query)

	random_number += 1

	return {"test_id": str(test_id), "subject": subject_from_json, "answer_keys": answer_keys_from_json, "submissions": []}, 201

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/tests/<scantron_id>/scantrons', methods =['POST'])
def upload_scantron(scantron_id):
	if 'data' not in request.files:
		print('No file part')
		return redirect(request.url)
	file = request.files['data']
	if file.filename == '':
		print('No selected file')
		return redirect(request.url)
	if allowed_file(file.filename) == False:
		print('File type not allowed')
		return redirect(request.url)
		
	filename = file.filename

	file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

	file.stream.seek(0)
	str_file = file.read().decode('utf-8')
	content = json.loads(str_file)
	print(content)
	answers_from_scantron = content["answers"]
	subject_from_scantron = content["subject"]
	uploaded_scantron_url = "http://localhost:5000" + url_for('uploaded_file', filename=filename)
	print(uploaded_scantron_url)

	my_exam = query_db("SELECT * FROM exam WHERE subject = ?", [subject_from_scantron], one=True)
	answer_keys_json = json.loads(my_exam['answer_keys'].replace("'", '"'))

	answers_result_dict = {}
	student_score = 0
	for question_no in answers_from_scantron:
		result_entry = {}
		if question_no in answers_from_scantron:
			result_entry["actual"] = answers_from_scantron[question_no]
		else:
			result_entry["actual"] = "null"
		if question_no in answer_keys_json:
			result_entry["expected"] = answer_keys_json[question_no]
		else:
			result_entry["expected"] = "null"
		answers_result_dict[question_no] = result_entry
		if result_entry["actual"] == result_entry["expected"]:
			student_score += 1

	answers_result_json = json.dumps(answers_result_dict).replace('"', '\'')
	insert_result = insert_db("INSERT INTO submission (scantron_id, scantron_url, name, subject, score, result) VALUES (?, ?, ?, ?, ?, ?)", [scantron_id, uploaded_scantron_url, content["name"], content["subject"], student_score, answers_result_json])

	my_test_result = query_db("SELECT * FROM submission WHERE scantron_id = ?", [scantron_id], one=True)
	my_test_result_json = json.loads(my_test_result['result'].replace("'", '"'))

	return {"scantron_id": my_test_result['scantron_id'], 
			"scantron_url": my_test_result['scantron_url'],
			"name": my_test_result['name'], 
			"subject": my_test_result['subject'],
			"score": my_test_result['score'],
			"result": my_test_result_json,
			#"answer_keys": answer_keys_json
			}, 201


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print("upload")
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/api/tests/<test_id>', methods =['GET'])
def all_submissions(test_id):
	my_exam = query_db("SELECT * FROM exam WHERE test_id = ?", [test_id], one=True)
	answer_keys_json = json.loads(my_exam['answer_keys'].replace("'", '"'))
	subject_name = my_exam['subject']

	my_test_submissions = query_db("SELECT * FROM submission WHERE subject = ?", [subject_name], one=False)
	my_test_submissions_json = []
	for my_submission in my_test_submissions:
		my_submission_json_str = json.dumps(my_submission)
		my_submission_json = json.loads(my_submission_json_str)
		my_submission_result_str = my_submission['result'].replace("'", '"')
		my_submission_result_json = json.loads(my_submission_result_str)
		my_submission_json['result'] = my_submission_result_json
		my_test_submissions_json.append(my_submission_json)

	return {"test_id": test_id,
			"subject": subject_name,
			"answer_keys": answer_keys_json, 
			"submissions": my_test_submissions_json
			}, 201


if __name__=='__main__':
	app.config['SESSION_TYPE'] = 'filesystem'
	app.run(debug = True)