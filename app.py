#!/usr/bin/python3
# imports
from flask import Flask, request, session, redirect, \
    url_for, render_template, flash, jsonify
# abort
from flask_api import status

# from flask_mysqldb import MySQL
#import collections
import MySQLdb
import os
# configuration of db

# create and initialise app
app = Flask(__name__, static_url_path='/static')
app.config['MYSQL_HOST'] = '176.58.96.74'
app.config['MYSQL_USER'] = 'comp4920'
app.config['MYSQL_PASSWORD'] = 'q3H286cJ5EXyGqRw'
app.config['MYSQL_DB'] = 'bookswapp'
app.config.from_object(__name__)  # config from above variables in file
# mysql = MySQL(app)  # attaches mysql object to the app?

# set the secret key
app.secret_key = os.urandom(24)


def connection():
    # mysql object holds credentials, use it to connect to db
    # conn = mysql.connection()
    conn = MySQLdb.connect(host=app.config['MYSQL_HOST'],
                           user=app.config['MYSQL_USER'],
                           passwd=app.config['MYSQL_PASSWORD'],
                           db=app.config['MYSQL_DB'])
    # c = mysql.connection.cursor()
    c = conn.cursor()
    return c, conn


# View to show entries on Flaskr
@app.route("/")
def index():
    todo = """Current API:
    /login - show login screen
    /logout - works
    /register - show registration form
    /api/user/login -> logs user in; basic function works, needs hashing
    /api/user/register -> Adds a new user to the database

    ========== Not yet confirmed working =============
    /api/user/<userid> -> Retrieves user information
    /api/user/list -> Lists all the users
    /api/books/create -> Adds a new book to the database
    /api/books/<bookid> -> Retrieves book information
    /api/books/list -> Lists all the books"""

    return render_template('index.html', todo=todo)


@app.route('/login')
def show_login_page():
    return render_template('login.html')


@app.route('/api/user/login', methods=['GET', 'POST'])
def login():
    """ User login/authentication/session management. """
    error = "Invalid email/password"

    # Should sanitate input and hash password
    # ...

    # Check that email and password fields are not empty
    if request.method == 'POST' and request.form['email'] and \
       request.form['password']:
        # Debugging: show input email
        # flash(request.form['email'])
        # flash(request.form['password'])
        query = ("SELECT * FROM User WHERE email = %s")
        email = "%s" % request.form['email']

        c, conn = connection()
        c.execute(query, [email])
        rv = c.fetchone()
        flash(rv)

        if rv:
            if request.form['password'] != rv[2]:
                error = "Invalid password"
            else:
                session['email'] = request.form['email']
                session['logged_in'] = True
                flash("Success: you are now logged in")
                # Back to list page on success with flash message
                return redirect(url_for('index'))
        else:
            error = "Invalid email"

    # Point this to home page with errors if they occurred
    return render_template('index.html', error=error)


@app.route('/logout')
def logout():
    """ User logout/authentication/session management. """
    session.pop('email', None)
    session.pop('logged_in', False)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/register')
def show_registration():
    return render_template('register.html')


@app.route('/api/user/register', methods=['GET', 'POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    university = request.form.get('university', None)
    location = request.form.get('location', None)

    c, con = connection()
    c.execute("SELECT * FROM User WHERE email = '%s'" % (email))
    rv = c.fetchall()

    # If the email already exists, throw an error code
    if len(rv) > 0:
        flash("This email already exists. Please pick a new one")
        c.close()
        con.close()
        return redirect(url_for('index')), status.HTTP_400_BAD_REQUEST
    # Create the user return success status
    else:
        q = """
            INSERT INTO User (email, password, university, location) VALUES
            ('{0}', '{1}', '{2}', '{3}')
            """.format(email, password, university, location)
        c.execute(q)
        con.commit()
        c.close()
        con.close()
        flash("Just registered new user. Details are:")
        flash(request.form['email'])
        flash(request.form['password'])
        flash(request.form['university'])
        flash(request.form['location'])
        return redirect(url_for('index')), status.HTTP_201_CREATED


# How will this be specified? TODO: figure out variable routing
@app.route('/api/user/<userid>')
def get_user(userid):
    c, con = connection()
    try:
        i = c.execute("SELECT * FROM User WHERE user_id = '{0}'".format(userid))
    except TypeError as e:
        flash(e)  # show in flash on next load
        return status.HTTP_400_BAD_REQUEST

    if int(i) > 0:
        values = c.fetchone()
        c.close()
        con.close()
        return jsonify({
            'User ID': values[0],
            'Email': values[1],
            'Password': values[2],
            'University': values[3],
            'Location': values[4]
            }), status.HTTP_200_OK
    c.close()
    con.close()
    return status.HTTP_204_NO_CONTENT


@app.route('/api/user/list')
def get_userlist():
    c, con = connection()
    c.execute('''SELECT * FROM User''')
    rv = c.fetchall()
    finalState = status.HTTP_204_NO_CONTENT

    # http://codehandbook.org/working-with-json-in-python-flask/
    userList = []
    for user in rv:
        userDict = {
            'User ID': user[0],
            'Email': user[1],
            'Password': user[2],
            'University': user[3],
            'Location': user[4]
        }
        userList.append(userDict)

    c.close()
    con.close()
    # set status code based on users found
    if len(userList) > 0:
        finalState = status.HTTP_200_OK
    return jsonify(userList), finalState


@app.route('/api/books/create', methods=['POST'])
def add_book():
    # Name/Author/isbn/prescribed_course/
    # pages*/edition/condition/transaction_type/price/description

    # Need to manage sessions here.
    # Removed previous session handling because it's not implemented yet.
    # MUST BE DEFINED

    if not session['logged_in']:
        return status.HTTP_400_BAD_REQUEST

    name = request.form['name']
    author = request.form['author']
    isbn = request.form['isbn']
    prescribed_course = request.form['prescribed_course']
    condition = request.form['condition']
    transaction_type = request.form['transaction_type']
    price = request.form['price']

    # OPTION PARAMS
    status = request.form.get('status', None)
    edition = request.form.get('edition', None)
    description = request.form.get('description', None)
    margin = request.form.get('margin', None)

    print("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (name, author, isbn, prescribed_course, edition, condition, transaction_type, status, price, margin, description))
    # How to signal fail - TODO: try except block?
    c, con = connection()

    # http://dev.mysql.com/doc/refman/5.7/en/keywords.html
    # 'condition' is a reserved keyboard, have to put it in backticks according to
    # http://stackoverflow.com/questions/21046293/error-in-sql-syntax-for-python-and-mysql-on-insert-operation
    query = ("INSERT INTO Book "
    "(name, author, isbn, prescribed_course, edition, `condition`, transaction_type, status, price, margin, description) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    values = (name, author, isbn, prescribed_course, edition, condition, transaction_type, status, price, margin, description)
    c.execute(query, values)

    con.commit()
    c.close()
    con.close()
    #return status.HTTP_201_CREATED
    return "Book created!"


@app.route('/api/books/<bookid>')
def get_book(bookid):
    c, con = connection()
    query = ("SELECT * FROM Book WHERE book_id = %s")
    c.execute(query, [bookid])
    rv = c.fetchone()

    if rv:
        c.close()
        con.close()
        return jsonify({
            'Book ID': rv[0],
            'Name': rv[1],
            'Author': rv[2],
            'ISBN': rv[3],
            'Prescribed Course': rv[4],
            'Edition': rv[5],
            'Condition': rv[6],
            'Transaction type': rv[7],
            'Status': rv[8],
            'Price': float(rv[9]), # Decimal is not JSON serializable error otherwise
            'Margin': float(rv[10]), # Decimal is not JSON serializable error otherwise
            'Description': rv[11],
            }), status.HTTP_200_OK
    else:
        c.close()
        con.close()
        return status.HTTP_404_NOT_FOUND


# Change type depending on which we want the list of: Selling/Wanted/Swap
@app.route('/api/books/list/<transaction_type>')
def get_booklist(transaction_type):
    c, con = connection()
    query = ("SELECT * FROM Book WHERE transaction_type = %s")
    c.execute(query, [transaction_type])
    rv = c.fetchall()

    # http://codehandbook.org/working-with-json-in-python-flask/
    bookList = []
    for book in rv:
        bookDict = {
            'Book ID': book[0],
            'Name': book[1],
            'Author': book[2],
            'ISBN': book[3],
            'Prescribed Course': book[4],
            'Edition': book[5],
            'Condition': book[6],
            'Transaction type': book[7],
            'Status': book[8],
            'Price': float(book[9]), # Decimal is not JSON serializable error otherwise
            'Margin': float(book[10]), # Decimal is not JSON serializable error otherwise
            'Description': book[11],
        }
        bookList.append(bookDict)

    # return json.dumps(userList)
    c.close()
    con.close()
    return jsonify(bookList), status.HTTP_200_OK


# @app.route('/test')
# def testJson():
    # return render_template('test.html')
# if __name__ == "__main__":
    app.run(debug=True)
