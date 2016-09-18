#!/usr/bin/python3
# imports
from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash, jsonify
import MySQLdb

# configuration of db
HOST = 'localhost'
USERNAME = 'root'
PASSWORD = 'cookies'


# create and initialise app
app = Flask(__name__)
app.config.from_object(__name__)
# @app.route("/")
# def hello():
#     return "Hello, World!"

# Connect to database


def connect_db():
    """ Connects to the Database. """
    conn = MySQLdb.Connect(HOST, USERNAME, PASSWORD)
    return conn

# @app.teardown_appcontext
# def close_db(error):
    # if connection is available, close it down

if __name__ == "__main__":
    connect_db()
    app.run()
