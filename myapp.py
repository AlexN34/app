#!/usr/bin/python3

from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
#app.config.from_object(__name__)
app.config['MYSQL_HOST'] = '176.58.96.74'
app.config['MYSQL_USER'] = 'comp4920'
app.config['MYSQL_PASSWORD'] = 'q3H286cJ5EXyGqRw'
app.config['MYSQL_DB'] = 'bookswapp'
mysql = MySQL(app)

@app.route("/")
def index():
    cur = mysql.connection.cursor()
    #cur.execute('''SELECT user, host FROM mysql.user''')
    cur.execute('''SELECT * FROM User''')
    rv = cur.fetchall()
    return str(rv)

if __name__ == "__main__":
    app.run()