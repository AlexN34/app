#!/usr/bin/python3
# imports
from flask import Flask, request, session, redirect, \
    url_for, render_template, flash, jsonify
# abort
from flask_api import status
from flask_cors import CORS, cross_origin
import time
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# from flask_mysqldb import MySQL
# import collections
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

# allow cross origin requests
CORS(app)


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


@app.route("/")
def index():
    todo = """Current API:
    /login - show login screen
    /logout - works
    /register - show registration form

    /api/user/login -> logs user in; basic function works, needs hashing
    /api/user/register -> Adds a new user to the database

    /api/user/<userid> -> Retrieves user information
    /api/user/list -> Lists all the users

    /api/books/create -> Adds a new book to the database
    /api/books/<bookid> -> Retrieves book information
    /api/books/list -> Lists all the books
    /api/books/search/<query> -> returns all results that any field matches

    /api/listings -> Shows which user owns which book"""

    if session.get('logged_in'):
        userid = session['user_id']
    else:
        userid = 0

        # Random login details while testing front-end
        session['logged_in'] = True
        session['user_id'] = 33
        session['email'] = "bread@gmail.com"
    return render_template('index.html', todo=todo, userid=userid)


# User login/authentication/session management.
@app.route('/api/user/login', methods=['GET', 'POST'])
def login():
    # Should sanitate input and hash password

    error = None

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
                token = generate_auth_token(rv[0])
                # session['email'] = request.form['email']
                # session['logged_in'] = True
                # session['user_id'] = rv[0]
                # flash("Success: you are now logged in")
                # Back to list page on success with flash message
                # return redirect(url_for('index'))
                return jsonify({
                    'status': 200,
                    'message': 'Login successful',
                    'user_id': rv[0],
                    'email': request.form['email'],
                    'token': token.decode('ascii'),
                    })
        else:
            error = "Invalid email"

    return login_error(error)
    # Point this to home page with errors if they occurred
    # return render_template('index.html', error=error)


@app.route('/logout')
def logout():
    """ User logout/authentication/session management. """
    session.pop('email', None)
    session.pop('logged_in', False)
    session.pop('user_id', None)
    flash('You were logged out')
    # return redirect(url_for('index'))
    return jsonify({
        'status': 200,
        'message': 'User logout successful',
        })


@app.route('/register')
def show_registration():
    return render_template('register.html')


@app.route('/api/user/register', methods=['GET', 'POST'])
def register():
    error = None

    email = request.form['email']
    password = request.form['password']
    university = request.form.get('university', None)
    location = request.form.get('location', None)

    c, con = connection()
    c.execute("SELECT * FROM User WHERE email = '%s'" % (email))
    rv = c.fetchall()

    # If the email already exists, throw an error code
    if len(rv) > 0:
        error = "Email already exists"
        c.close()
        con.close()
        # return redirect(url_for('index')), status.HTTP_400_BAD_REQUEST
        return registration_error(error)

    # Create the user return success status
    else:
        # This format supposedly prevents SQL injections
        query = ("INSERT INTO User "
                 "(email, password, university, location) "
                 "VALUES (%s, %s, %s, %s)")
        values = (email, password, university, location)
        c.execute(query, values)

        con.commit()
        c.close()
        con.close()

        flash("Just registered new user. Details are:")
        flash(request.form['email'])
        flash(request.form['password'])
        flash(request.form['university'])
        flash(request.form['location'])
        # return redirect(url_for('index')), status.HTTP_201_CREATED
        return jsonify({
            'status': 201,
            'message': 'User registration successful',
            }), status.HTTP_201_CREATED


@app.route('/api/user/<userid>')
def get_user(userid):
    c, con = connection()
    query = ("SELECT * FROM User WHERE user_id = %s")
    c.execute(query, [userid])
    rv = c.fetchone()
    c.close()
    con.close()

    if rv:
        return jsonify({
            'user_id': rv[0],
            'email': rv[1],
            'password': rv[2],
            'university': rv[3],
            'location': rv[4],
            })

    return not_found()


# @app.route('/api/user/update/<userid>', methods=['PUT'])
# Using POST method for now for easier testing
@app.route('/api/user/update/<userid>', methods=['POST'])
def update_user(userid):
    message = ''

    # # Check user is logged in
    # if not session.get('logged_in'):
    #     return not_logged_in()

    # # Check logged in user is the one being updated
    # if str(userid) != str(session['user_id']):
    #     return not_auth()

    # Check user is logged in (has a valid token)
    if not verify_auth_token(request.form['token']):
        return not_logged_in()

    # Check the user being updated is the same as the logged in user from the token
    if (str(userid) != str(verify_auth_token(request.form['token']))):
        return not_auth()


    c, con = connection()

    # Should validate/sanitise fields
    # if (request.form['email']):
    if ('email' in request.form):
        query = ("UPDATE User SET email = %s WHERE user_id = %s")
        values = (request.form['email'], userid)
        c.execute(query, values)
        session['email'] = request.form['email']
        message += "Email updated\n"

    # if (request.form['password']):
    if ('password' in request.form):
        query = ("UPDATE User SET password = %s WHERE user_id = %s")
        values = (request.form['password'], userid)
        c.execute(query, values)
        message += "Password updated\n"

    # if (request.form['university']):
    if ('university' in request.form):
        query = ("UPDATE User SET university = %s WHERE user_id = %s")
        values = (request.form['university'], userid)
        c.execute(query, values)
        message += "University updated\n"

    # if (request.form['location']):
    if ('location' in request.form):
        query = ("UPDATE User SET location = %s WHERE user_id = %s")
        values = (request.form['location'], userid)
        c.execute(query, values)
        message += "Location updated\n"

    con.commit()
    c.close()
    con.close()
    return jsonify({
        'status': 200,
        'message': message,
        })


# @app.route('/api/user/delete/<userid>', methods=['DELETE'])
# Using GET method for now for easier testing
@app.route('/api/user/delete/<userid>', methods=['POST'])
def delete_user(userid):
    # Check user is logged in
    # if not session.get('logged_in'):
    #     return not_logged_in()

    # # Check logged in user is the one being deleted
    # if str(userid) != str(session['user_id']):
    #     return not_auth()

    # Check user is logged in (has a valid token)
    if not verify_auth_token(request.form['token']):
        return not_logged_in()

    # Check the user being updated is the same as the logged in user from the token
    if (str(userid) != str(verify_auth_token(request.form['token']))):
        return not_auth()

    c, con = connection()

    # Delete all book listings under this user
    query = ("SELECT * FROM Book_List WHERE user_id = %s")
    c.execute(query, [userid])
    rv = c.fetchall()

    for listing in rv:
        bookid = listing[2]
        query = ("DELETE FROM Book WHERE book_id = %s")
        c.execute(query, [bookid])

    query = ("DELETE FROM Book_List WHERE user_id = %s")
    c.execute(query, [userid])

    # Delete the account itself
    query = ("DELETE FROM User WHERE user_id = %s")
    c.execute(query, [userid])

    con.commit()
    c.close()
    con.close()
    logout()
    return jsonify({
        'status': 200,
        'message': 'User deleted',
        })


@app.route('/api/user/list')
def get_userlist():
    c, con = connection()
    c.execute('''SELECT * FROM User''')
    rv = c.fetchall()
    c.close()
    con.close()
    finalState = status.HTTP_204_NO_CONTENT

    # http://codehandbook.org/working-with-json-in-python-flask/
    userList = []
    for user in rv:
        userDict = {
            'user_id': user[0],
            'email': user[1],
            'password': user[2],
            'university': user[3],
            'location': user[4]
        }
        userList.append(userDict)

    # set status code based on users found
    if len(userList) > 0:
        finalState = status.HTTP_200_OK
    return jsonify(userList), finalState


@app.route('/api/books/create', methods=['POST'])
def add_book():
    # if not session.get('logged_in'):
    #     return not_logged_in()

    # Check user is logged in (has a valid token)
    if not verify_auth_token(request.form['token']):
        return not_logged_in()

    userid = verify_auth_token(request.form['token'])

    name = request.form['name']
    author = request.form['author']
    prescribed_course = request.form['prescribed_course']
    condition = request.form['condition']
    transaction_type = request.form['transaction']
    price = request.form['price']

    # Optional parameters
    isbn = request.form.get('isbn', None)
    bookStatus = request.form.get('status', None)
    edition = request.form.get('edition', None)
    description = request.form.get('description', None)
    # margin = request.form.get('margin', None)

    c, con = connection()
    # http://dev.mysql.com/doc/refman/5.7/en/keywords.html
    # 'condition' is a reserved keyboard, have to put it in backticks
    # http://stackoverflow.com/questions/21046293/
    # error-in-sql-syntax-for-python-and-mysql-on-insert-operation
    query = ("INSERT INTO Book "
             "(name, author, isbn, prescribed_course, edition, `condition`, "
             "transaction_type, price, description) "
             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    values = (name, author, isbn, prescribed_course, edition, condition,
              transaction_type, price, description)
    c.execute(query, values)

    # Mark book listing as belonging to user
    book_id = c.lastrowid  # Get the id of the newly inserted book
    query = ("INSERT INTO Book_List (user_id, book_id, `date`)"
             "VALUES (%s, %s, %s)")
    # print(time.strftime('%Y-%m-%d %H:%M:%S'))
    # values = (session['user_id'], book_id, time.strftime('%Y-%m-%d %H:%M:%S'))
    values = (userid, book_id, time.strftime('%Y-%m-%d %H:%M:%S'))

    c.execute(query, values)

    con.commit()
    c.close()
    con.close()
    return jsonify({
        'status': 201,
        'message': 'Book created',
        }), status.HTTP_201_CREATED


# @app.route('/api/books/delete/<bookid>', methods=['DELETE'])
# Using GET method for now for easier testing
@app.route('/api/books/delete/<bookid>', methods=['POST'])
def delete_book(bookid):
    # Check user is logged in, and that they own the associated book listing
    # if not session.get('logged_in'):
    #     return not_logged_in()

    # Check user is logged in (has a valid token)
    if not verify_auth_token(request.form['token']):
        return not_logged_in()

    c, con = connection()
    query = ("SELECT * FROM Book_List WHERE book_id = %s")
    c.execute(query, [bookid])
    rv = c.fetchone()

    # if (rv[0] != session['user_id']):
    #     return not_auth()

    if rv:
        # Check the user being updated is the same as the logged in user from the token
        if (str(rv[1]) != str(verify_auth_token(request.form['token']))):
            return not_auth()

        query = ("DELETE FROM Book WHERE book_id = %s")
        c.execute(query, [bookid])
        query = ("DELETE FROM Book_List WHERE book_id = %s")
        c.execute(query, [bookid])
        con.commit()
        c.close()
        con.close()
        return jsonify({
            'status': 200,
            'message': 'Book deleted',
            })

    return not_found()


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
            'book_id': rv[0],
            'name': rv[1],
            'author': rv[2],
            'isbn': rv[3],
            'course': rv[4],
            'edition': rv[5],
            'condition': rv[6],
            'trans_type': rv[7],
            'status': rv[8],
            # Decimal is not JSON serializable error otherwise (below 2)
            'price': float(rv[9]),
            'margin': float(rv[10]),
            'description': rv[11],
            }), status.HTTP_200_OK
    else:
        c.close()
        con.close()
        return not_found()


@app.route('/api/books/search/<query>')
def book_search(query):
    c, con = connection()
    search_string = '\'%' + query + '%\''
    # values = (search_string, search_string, search_string, search_string)
    q = ("SELECT * FROM Book WHERE (name LIKE {0} OR author LIKE {1} "
         "OR isbn LIKE {2} "
         "OR prescribed_course LIKE {3})").format(search_string,
                                                  search_string,
                                                  search_string, search_string)
    c.execute(q)
    rv = c.fetchall()

    c.close()
    con.close()
    finalState = status.HTTP_204_NO_CONTENT
    # http://codehandbook.org/working-with-json-in-python-flask/
    bookList = []
    for book in rv:
        bookDict = {
            'book_id': book[0],
            'name': book[1],
            'author': book[2],
            'isbn': book[3],
            'course': book[4],
            'edition': book[5],
            'condition': book[6],
            'trans_type': book[7],
            'status': book[8],
            # Decimal is not JSON serializable error otherwise
            'price': float(book[9]),
            'margin': float(book[10]),
            'description': book[11],
        }
        bookList.append(bookDict)

    if len(bookList) > 0:
        finalState = status.HTTP_200_OK
    return jsonify(bookList), finalState


# Change type depending on which we want the list of: Selling/Wanted/Swap
# transaction_type = sell, buy, swap or all
@app.route('/api/books/list/<transaction_type>')
def get_booklist(transaction_type):
    c, con = connection()

    if transaction_type == "all":
        query = ("SELECT * FROM Book")
        c.execute(query)
    else:
        query = ("SELECT * FROM Book WHERE transaction_type = %s")
        c.execute(query, [transaction_type])

    rv = c.fetchall()
    # http://codehandbook.org/working-with-json-in-python-flask/
    bookList = []
    for book in rv:
        bookDict = {
            'book_id': book[0],
            'name': book[1],
            'author': book[2],
            'isbn': book[3],
            'course': book[4],
            'edition': book[5],
            'condition': book[6],
            'trans_type': book[7],
            'status': book[8],
            # Decimal is not JSON serializable error otherwise below
            'price': float(book[9]),
            'margin': float(book[10]),
            'description': book[11],
        }
        bookList.append(bookDict)

    c.close()
    con.close()
    return jsonify(bookList)


# Testing purposes
@app.route('/api/listings')
def get_listings():
    c, con = connection()
    query = ("SELECT * FROM Book_List")
    c.execute(query)
    rv = c.fetchall()

    listings = []
    for item in rv:
        listingDict = {
            'listing_id': item[0],
            'user_id': item[1],
            'book_id': item[2],
            'date': item[3],
        }
        listings.append(listingDict)

    c.close()
    con.close()
    return jsonify(listings)

# Testing JOIN
@app.route('/api/booklistings')
def get_book_listings():
    c, con = connection()
    query = ("SELECT User.user_id, User.email, Book_List.id, Book_List.date, Book.* "
                "FROM Book_List "
                "INNER JOIN Book "
                "ON Book_List.book_id=Book.book_id "
                "INNER JOIN User "
                "ON Book_List.user_id=User.user_id "
                "WHERE Book.status='available'")
    c.execute(query)
    rv = c.fetchall()

    listings = []
    for item in rv:
        listingDict = {
            'user_id': item[0],
            'email': item[1],
            'listing_id': item[2],
            'date': item[3],
            'book_id': item[4],
            'name': item[5],
            'author': item[6],
            'isbn': item[7],
            'course': item[8],
            'edition': item[9],
            'condition': item[10],
            'trans_type': item[11],
            'status': item[12],
            'price': float(item[13]),
            'margin': float(item[14]),
            'description': item[15],
        }
        listings.append(listingDict)

    c.close()
    con.close()
    return jsonify(listings)

@app.route('/api/booklistings/<bookid>')
def get_book_listing(bookid):
    c, con = connection()
    query = ("SELECT User.user_id, User.email, Book_List.id, Book_List.date, Book.* "
                "FROM Book_List "
                "INNER JOIN Book "
                "ON Book_List.book_id=Book.book_id "
                "INNER JOIN User "
                "ON Book_List.user_id=User.user_id "
                "WHERE Book.status='available' AND Book.book_id = %s")
    c.execute(query, [bookid])
    rv = c.fetchone()

    if rv:
        c.close()
        con.close()
        return jsonify({
            'user_id': rv[0],
            'email': rv[1],
            'listing_id': rv[2],
            'date': rv[3],
            'book_id': rv[4],
            'name': rv[5],
            'author': rv[6],
            'isbn': rv[7],
            'course': rv[8],
            'edition': rv[9],
            'condition': rv[10],
            'trans_type': rv[11],
            'status': rv[12],
            'price': float(rv[13]),
            'margin': float(rv[14]),
            'description': rv[15],
        })

    c.close()
    con.close()
    return not_found()



# @app.route('/api/request/<book_id>')
# def request_book(book_id):
#     # TODO how to retrieve requesting user? Assume retrieving from a form
#     buying_user_id = request.form['buying_user_id']
#     price = request.form['price']
#     request_status = "Pending"
#     c, con = connection()
#     query = ("SELECT * FROM Book_List WHERE book_id = %s" % (book_id))
#     c.execute(query)
#     rv = c.fetchall()
#     if rv:
#         selling_user_id = rv[0][1]  # TODO make cleaner
#         query = ("INSERT INTO Transaction_List "
#                  "(buying_user_id, selling_user_id, price, status)"
#                  "VALUES (%s, %s, %s, %s)")
#         values = (buying_user_id, selling_user_id, price, request_status)
#         c.execute(query, values)

#         """ Does Transaction List need to know book ID/transaction? how to match
#             Notification with Transaction List to retrieve price? """
#         query = ("INSERT INTO Notification "
#                  "(user_id, book_id)"
#                  "VALUES (%s, %s)")
#         values = (selling_user_id, book_id)
#         c.execute(query, values)
#         con.commit()
#         c.close()
#         con.close()

#     else:
#         return not_found()

@app.route('/api/request/<book_id>', methods=['POST'])
def request_book(book_id):
    # TODO how to retrieve requesting user? Assume retrieving from a form
    # Check token
    if not verify_auth_token(request.form['token']):
        return not_logged_in()

    buying_user_id = str(verify_auth_token(request.form['token']))
    request_status = "pending"
    bookid = str(book_id)

    c, con = connection()
    query = ("SELECT * FROM Book_List WHERE book_id = %s")
    c.execute(query, [bookid])
    rv = c.fetchall()

    if rv: # book exists
        print ("Message")
        #print (vars(rv))
        print (rv[0])
        selling_user_id = rv[1]

        query = ("INSERT INTO Transaction (Buying_User_Id, Selling_User_Id, Book_Id, Status) "
                 "VALUES (%s, %s, %s, %s)")
        values = (buying_user_id, selling_user_id, book_id, request_status)
        c.execute(query, values)

        transaction_id = c.lastrowid
        query = ("INSERT INTO Notification "
                 "(User_Id, Transaction_Id) "
                 "VALUES (%s, %s)")
        values = (selling_user_id, transaction_id)
        c.execute(query, values)
        con.commit()
        c.close()
        con.close()
        return jsonify({
            'status': 201,
            'message': 'Request sent',
            }), status.HTTP_201_CREATED
    else:
        return not_found()

# @app.route('/api/respond/<book_id>')
# def respond_book(notification_id):

@app.route('/api/request/notifications/<user_id>')
def get_notifications(user_id):
    c, con = connection()
    query = ("SELECT Transaction.*, Notification.* "
                "FROM Transaction "
                "INNER JOIN Notification "
                "ON Transaction.Selling_User_Id=Notification.User_Id "
                "WHERE Transaction.Status='pending' AND Transaction.Selling_User_Id = %s")
    c.execute(query, [user_id])
    rv = c.fetchall()

    notif = []
    for item in rv:
        notifDict = {
            'notification_id': item[0],
            'selling_user_id': item[1],
            'buying_user_id': item[2],
            'status': item[3],
            'book_id': item[4],
            'notification_id1': item[5],
            'user_id': item[6],
            'transaction_id': item[7],
        }
        notif.append(notifDict)

    c.close()
    con.close()
    return jsonify(notif)

# https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
# Generates a token with the user_id as data and an expiration time of 10 minutes
def generate_auth_token(user_id, expiration = 600):
    s = Serializer(app.secret_key, expires_in = expiration)
    return s.dumps({ 'user_id': user_id })

# Verifies the token is valid and not expired, and returns the user_id 
def verify_auth_token(token):
    s = Serializer(app.secret_key)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None
    except BadSignature: 
        return None
    return data['user_id']

# Error handlers
# @app.errorhandler(400)
def registration_error(error):
    message = {
        'status': 400,
        'error': error,
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp


# @app.errorhandler(401)
def login_error(error):
    message = {
        'status': 401,
        'error': error,
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


# @app.errorhandler(401)
def not_logged_in():
    message = {
        'status': 401,
        'error': 'Not logged in',
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp


# @app.errorhandler(403)
def not_auth():
    message = {
        'status': 403,
        'error': 'Logged in but probably '
                 'attempting to do something with another user id',
    }
    resp = jsonify(message)
    resp.status_code = 403
    return resp


# @app.errorhandler(404)
def not_found():
    message = {
        'status': 404,
        'error': 'Not found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

# @app.route('/test')
# def testJson():
    # return render_template('test.html')
if __name__ == "__main__":
    app.run(debug=True)
