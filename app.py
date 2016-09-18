#!/usr/bin/python3
# imports
from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash, jsonify

#configuration of db
USERNAME = 'root'
PASSWORD = 'cookies'


#create and initialise app
app = Flask(__name__)
app.config.from_object(__name__)

# @app.route("/")
# def hello():
#     return "Hello, World!"

if __name__ == "__main__":
    app.run()
