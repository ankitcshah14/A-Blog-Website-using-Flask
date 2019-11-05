from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
# __name__ is a special variable in python which is the name of the module
# Learn about decorators(@)


# We need to define a secret key to prevent cookies from getting modified and also protecting the website
# against any forgery attacks etc.

# This random string has been generated using secrets.token_hex(16)
app.config['SECRET_KEY'] = 'e789d02eeb0875c93c93995dc6aeef9f'

# To connect to the database we use SQLAlchemy which is a very popular ORM(Object Relational Mapping)
# It allows us to access the database in an object oriented way. Biggest advantage is one can
# use different Databases without changing the python code.
# In this series we use a SQLite Database for development and a Postgres Database for Deployment
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# The "///" gives a relative path.

# Creating the limiter instance
limiter = Limiter(app, key_func=get_remote_address)

# Creating Database Instance
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
loginManager = LoginManager(app)
loginManager.login_view = 'login'
loginManager.login_message_category = 'info'  # Bootstrap class just to make it look better

# The following configurations are required to send an email over the internet
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# To hide sensitive info we can even save username and password in environment variables
# To know more watch Corey Schafer's video on it
app.config['MAIL_USERNAME'] = 'ankitcshah14@gmail.com'
app.config['MAIL_PASSWORD'] = '26460429'
mail = Mail(app)

from flaskblog import routes

'''
To create the Database:
1) Open terminal and navigate to your directory where you want to create the Database
2) Run python3
4) from flaskblog.py import db(Basically the db instance)
5) db.create_all() should create the db in your current working directory
'''
