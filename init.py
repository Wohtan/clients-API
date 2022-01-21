import enum
from sys import setrecursionlimit
from unittest.util import sorted_list_difference
import flask
from flask import request, render_template, redirect, url_for, flash, session
import sqlite3
from math import ceil
from flask.templating import render_template_string
from functions import *
from forms import *

##Login utils:
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from models import *
from werkzeug.urls import url_parse

app = flask.Flask(__name__)

# if __name__ == "__main__":
#     app.config["DEBUG"] = True

app.debug = True

app.secret_key = "keypass"
login_manager = LoginManager(app)
login_manager.login_view = "/api/v1/login"

