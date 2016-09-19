#!/usr/bin/python3
# imports
from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash, jsonify
import MySQLdb

# configuration of db

HOST = '176.58.96.74'
USERNAME = 'comp4920'
PASSWORD = 'q3H286cJ5EXyGqRwcookies'


# create and initialise app
app = Flask(__name__)
app.config.from_object(__name__)

# View to show entries on Flaskr


@app.route("/")
def index():
    """Searches the database for entries, then displays them."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Book_List;')
    entries = cursor.fetchall()
    return render_template('index.html', entries=entries)
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
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Book_List (user_id, book_id) values (0, 5);')
    cursor.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))


def connect_db():
    """ Connects to the Database. """
    conn = MySQLdb.Connect(HOST, USERNAME, PASSWORD)
    cursor = conn.cursor()
    cursor.execute('use flaskTest;')
    return conn

# @app.teardown_appcontext


def close_db(connection):
    # if connection is available, close it down
    try:
        connection.cursor.close()
        connection.close()
    except MySQLdb.Error as e:
        print("ERROR %d IN CLOSE: %s" % (e.args[0], e.args[1]))


if __name__ == "__main__":
    app.run()
