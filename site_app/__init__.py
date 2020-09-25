# from . import *
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from site_app import site_config
from flask_migrate import Migrate
from flask_login import LoginManager
import os
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = site_config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
migrate = Migrate(app, db, compare_type=True)

login = LoginManager(app)
login.login_view = 'login'

from site_app import models
from site_app.routes import main_routes, autocomplete, patients, smo_expert_defects_routes, reference_routes
from site_app.routes.reports import main_reports_routes
from site_app.models.main_tables import DefectList



