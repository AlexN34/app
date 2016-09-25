#!/usr/bin/python3

from flask import Flask, json, jsonify
from flask_mysqldb import MySQL
import collections

app = Flask(__name__)
#app.config.from_object(__name__)
app.config['MYSQL_HOST'] = '176.58.96.74'
app.config['MYSQL_USER'] = 'comp4920'
app.config['MYSQL_PASSWORD'] = 'q3H286cJ5EXyGqRw'
app.config['MYSQL_DB'] = 'bookswapp'
mysql = MySQL(app)

@app.route("/")
def index():
    return get_user_table()

# Returns user table as a JSON object - change for other tables?
def get_user_table():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM User''')
    rv = cur.fetchall()

    # http://codehandbook.org/working-with-json-in-python-flask/
    userList = []
    for user in rv:
        # http://stackoverflow.com/questions/15711755/converting-dict-to-ordereddict
        userDict = (
            ('User ID', user[0]),
            ('Email', user[1]),
            ('Password' , user[2]),
            ('University', user[3]),
            ('Location', user[4])
        )
        userDict = collections.OrderedDict(userDict)
        userList.append(userDict)

    #return json.dumps(userList)
    return jsonify(userList) # Pretty printing


if __name__ == "__main__":
    app.run()