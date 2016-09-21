#!/usr/bin/python3
# imports
from flask import Flask, request, session, redirect, \
    url_for, abort, render_template, flash, jsonify
# import json  # possibly put back in if needed
from flask_mysqldb import MySQL
import MySQLdb
import collections

# configuration of db


# create and initialise app
app = Flask(__name__)
app.config['MYSQL_HOST'] = '176.58.96.74'
app.config['MYSQL_USER'] = 'comp4920'
app.config['MYSQL_PASSWORD'] = 'q3H286cJ5EXyGqRw'
app.config['MYSQL_DB'] = 'bookswapp'
mysql = MySQL(app)  # attaches mysql object to the app?
app.config.from_object(__name__)


# View to show entries on Flaskr
@app.route("/")
def index():
    # """Searches the database for entries, then displays them."""
    # cur = connect_db()
    # cur.execute('SELECT * FROM Book_List;')
    # entries = cur.fetchall()
    # return str(entries)  # check what comes back
    return get_user_table()  # check what comes back
    # return render_template('index.html', entries=entries)
# Connect to database


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ User login/authentication/session management. """
    error = None
    if request.method == 'POST':  # request is imported module
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid username"
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid password"
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
        return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """ User logout/authentication/session management. """
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_entry():
    """ Add new post to database. """
    if not session._get('logged_in'):
        abort(401)
    try:
        cur = connect_db()
        cur.execute('INSERT INTO Book_List (user_id, book_id) values (0, 5);')
        cur.commit()
        flash('New entry was successfully posted')
        return redirect(url_for('index'))
    except MySQLdb.DatabaseError as e:
        print("ERROR %d IN ADDING: %s" % (e.args[0], e.args[1]))


# Returns user table as a JSON object - change for other tables?
def get_user_table():
    cur = connect_db()
    cur.execute('''SELECT * FROM Book''')
    rv = cur.fetchall()

    # http://codehandbook.org/working-with-json-in-python-flask/
    userList = []
    for user in rv:
        # http://stackoverflow.com/questions/15711755/converting-dict-to-ordereddict
        userDict = (
            ('User ID', user[0]),
            ('Email', user[1]),
            ('Password', user[2]),
            ('University', user[3]),
            ('Location', user[4])
        )
        userList.append(collections.OrderedDict(userDict))

    # return json.dumps(userList)
    return jsonify(userList)  # Pretty printing


def connect_db():
    """ Connects to the Database. """
    cur = mysql.connection.cursor()
    cur.execute('use bookswapp;')
    return cur

# @app.teardown_appcontext


# Connection closed for you in Flask-MySQL
# def close_db(connection):
    # # if connection is available, close it down
    # try:
    # connection.cursor.close()
    # connection.close()
    # except MySQLdb.Error as e:
    # print("ERROR %d IN CLOSE: %s" % (e.args[0], e.args[1]))


if __name__ == "__main__":
    app.run(debug=True)
