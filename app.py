# Import necessary packages
from flask import Flask, json, request, redirect, url_for, session, jsonify
import json
from flaskext.mysql import MySQL
import pymysql
from werkzeug.wrappers import response
import hashlib as hs
from flask_cors import CORS as cors


# Create vars for Flask and MySQL
app = Flask(__name__)
cors(app=app)
sql_var = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345'
app.config['MYSQL_DATABASE_DB'] = 'gradeseeker'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

sql_var.init_app(app)

@app.route("/classes", methods=["POST"])
def classes():
    sql_connect = sql_var.connect()
    cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

    crn = request.form.get('crn')

    try: 
        cursor.execute("SELECT p.firstName, p.lastName, t.semester FROM teaches t JOIN professors p ON t.profId=p.id WHERE t.crn=%s", crn)
        rows = cursor.fetchall()      
                
        if rows != None:
            print(rows)
            resp = jsonify(rows)
            resp.status_code = 200
            resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            resp.headers.add('Access-Control-Allow-Origin', '*')
            resp.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

            return resp

    except Exception as e:
        resp = jsonify(e)
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

        return resp

    finally:
        cursor.close()
        sql_connect.close()


@app.route("/prof", methods=["POST"])
def prof():
    sql_connect = sql_var.connect()
    cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

    cat = request.form.get('Category')
    id = request.form.get('ID')

    try: 
        if(cat == "classes"):
            cursor.execute("SELECT crn, semester FROM teaches WHERE profId=%s", id)
            rows = cursor.fetchall()
        if(cat== "average"):
            cursor.execute("SELECT t.profId, ROUND(AVG(s.averageGPA), 2) AS av FROM teaches t NATURAL JOIN grades g NATURAL JOIN statistics s GROUP BY t.profId=%s", id)
            rows = cursor.fetchone()
        
        
        
        if rows != None:
            resp = jsonify(rows)
            resp.status_code = 200
            resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            resp.headers.add('Access-Control-Allow-Origin', '*')
            resp.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

            return resp

    except Exception as e:
        resp = jsonify(e)
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

        return resp

    finally:
        cursor.close()
        sql_connect.close()


@app.route("/browse", methods=["POST"])
def browse():
    sql_connect = sql_var.connect()
    cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

    cat = request.form.get('Category')
    off = int(request.form.get('Offset'))

    try: 
        if(cat == "professors"):
            cursor.execute("SELECT p.id, p.firstName, p.lastName, r.ratings FROM professors p JOIN ratings r ON p.id=r.profId LIMIT 20 OFFSET " + str(off*20))
        else:
            cursor.execute("SELECT c.crn, c.courseCode, c.courseTitle, ROUND(AVG(s.averageGPA), 2) AS av FROM courses c NATURAL JOIN grades g JOIN statistics s ON s.gradeId=g.gradeId GROUP BY g.crn LIMIT 20 OFFSET " + str(off*20))
        # SELECT p.firstName, p.lastName, r.ratings FROM professors p JOIN ratings r ON p.id=r.profId LIMIT 20 OFFSET 0 
        #
        rows = cursor.fetchall()

        if rows != None:
            resp = jsonify(rows)
            resp.status_code = 200
            resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            resp.headers.add('Access-Control-Allow-Origin', '*')
            resp.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

            return resp

    except Exception as e:
        resp = jsonify(e)
        resp.status_code = 400
        resp.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

        return resp

    finally:
        cursor.close()
        sql_connect.close()

# App route for /login.
@app.route("/login", methods=["GET"])
def login():

    # Create connection to SQL server. 
    sql_connect = sql_var.connect()
    cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

    try:

        # Get details from request
        req = request.get_json()
        user_id = req["user_id"]
        user_pass = req["user_pass"]

        print(req)

        print(user_id + "\n" + user_pass)
        #user_id = "admin"
        #user_pass = "7253e9cb94e77341954eb6e593b0aa13aa99371305ef5e8c2f81fb3aaa4b11a1"

        cursor.execute("SELECT U.passwordHash FROM userInfo U WHERE U.userId=%s", user_id)
        rows = cursor.fetchone()

        if rows != None and rows["passwordHash"] == user_pass:

            # Respond to request with successful log in. 
            resp = resp = jsonify(login_attempt=1)
            resp.status_code = 200
            return resp
        else:

            # Incorrect login information provided.
            resp = resp = jsonify(login_attempt=0)
            return resp

    except Exception as e:

        # Return error message
        resp = jsonify(error=e)
        resp.status_code = 400

        return resp

    finally:

        # Close cursor
        cursor.close()
        sql_connect.close()

# App route for logout.
@app.route("/logout")
def logout():
    return "Hello, World!"

# App route for /signup.
@app.route("/signup", methods=["POST"])
def signup():

    # Create connection to SQL server. 
    sql_connect = sql_var.connect()
    cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

    try:

        # Get data from user.
        req = request.get_json()
        user_fname = req["user_fname"]
        user_lname = req["user_lname"]
        user_id = req["user_id"]
        user_pass = req["user_pass"]

        cursor.execute("SELECT U.userId, U.passwordHash FROM userInfo U WHERE U.userId=%s", user_id)
        rows = cursor.fetchone()

        print(rows)

        if rows == None and request.method == "POST":

            # Insert user into userInfo
            cursor.execute("INSERT INTO userInfo VALUES(%s, %s, %s, %s, %s);", (user_id, user_fname, user_lname, user_pass, user_id))
            sql_connect.commit()

            resp = jsonify(signup_attempt=1)
            resp.status_code = 200

            return resp
        else:

            # User with given user id already exists. Return response with this message
            resp = jsonify(signup_attempt=0)
            resp.status_code = 400

            return resp

    except Exception as e:

        # Catch error and return it. 
        resp = jsonify(error=e)
        resp.status_code = 400

        return resp
    finally:

        # Close cursors and the sql conenction. 
        cursor.close()
        sql_connect.close()

# App route for searching courses by course code, i.e. CS411, ECE220, and so on.
@app.route("/search/class/<course_code>", methods=["GET"])
def get_course(course_code):
    if request.method == "GET":

        # Initiate SQL server connection
        sql_connect = sql_var.connect()
        cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

        # Query for pulling data from database based on course_code
        query = """SELECT C.courseCode, C.courseTitle
                   FROM courses C
                   WHERE C.courseCode=%s
                   GROUP BY C.courseCode;"""

        cursor.execute(query, course_code)
        rows = cursor.fetchmany()
        
        resp = jsonify(data = json.dumps(rows))

        resp.status_code = 200

        # Close SQL connection
        cursor.close()
        sql_connect.close()

        return resp
    else:
        resp = jsonify("Invalid request method")
        resp.status_code = 400

        return resp


# App route for searching classes by professor name.
@app.route("/search/professor/<professor_name>", methods=["GET"])
def get_professor(professor_name):
    if request.method == "GET":

        # Initiate SQL server connection
        sql_connect = sql_var.connect()
        cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

        # Query for pulling data from database based on course_code
        query = """SELECT *
                    FROM %s"""

        cursor.execute(query, professor_name)
        rows = cursor.fetchmany()
        
        resp = jsonify(data = json.dumps(rows))

        resp.status_code = 200

        # Close SQL connection
        cursor.close()
        sql_connect.close()

        return resp
    else:
        resp = jsonify("Invalid request method")
        resp.status_code = 400

        return resp

# App route for searching classes by CRN (course registration number).
@app.route("/search/crn/<crn_val>", methods=["GET"])
def get_class_by_crn(crn_val):
    if request.method == "GET":

        # Initiate SQL server connection
        sql_connect = sql_var.connect()
        cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

        # Query for pulling data from database based on course_code
        query = """SELECT C.crn, C.courseCode, C.courseTitle
                   FROM courses C
                   WHERE C.crn = %s;"""

        cursor.execute(query, crn_val)
        rows = cursor.fetchmany()
        
        resp = jsonify(data = json.dumps(rows))

        resp.status_code = 200

        # Close SQL connection
        cursor.close()
        sql_connect.close()

        return resp
    else:
        resp = jsonify("Invalid request method")
        resp.status_code = 400

        return resp

# App route to view and update a user's profile.
@app.route("/userprofile=<user_id>", methods=["GET", "POST"])
def get_profile(user_id):
    # Initiate SQL server connection
    sql_connect = sql_var.connect()
    cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

    if request.method == "GET":

        query = """SELECT U.firstName, U.lastName
                   FROM userInfo U
                   WHERE U.userId=%s"""
        
        cursor.execute(query, user_id)
        rows = cursor.fetchone()

        resp = jsonify(firstName = rows["firstName"], lastName = rows["lastName"])
        resp.status_code = 200

        # Close SQL connection
        cursor.close()
        sql_connect.close()

        return resp

    else:

        req = request.get_json()
        user_ufname = req["user_ufname"]
        user_ulname = req["user_ulname"]
        user_upass = req["user_upass"]

        cursor.execute("UPDATE userInfo U SET U.firstName=%s, U.lastName=%s, U.passwordHash=%s WHERE U.userId=%s",(user_ufname, user_ulname, user_upass, user_id))
        sql_connect.commit()

        # Close SQL connection
        cursor.close()
        sql_connect.close()

        resp = jsonify(update=1)
        resp.status_code = 200

        return resp

@app.route("/delete=<user_id>", methods=["POST"])
def del_user(user_id):
    if request.method == "POST":
        # Initiate SQL server connection
        sql_connect = sql_var.connect()
        cursor = sql_connect.cursor(pymysql.cursors.DictCursor)

        cursor.execute("DELETE FROM userInfo U WHERE U.userId=%s", user_id)
        sql_connect.commit()

        # Close SQL connection
        cursor.close()
        sql_connect.close()

        resp = jsonify(deleted=1)
        resp.status_code = 200

        return resp

