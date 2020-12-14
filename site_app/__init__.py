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
from site_app.routes import main_routes, autocomplete, patients, smo_expert_defects_routes, reference_routes,\
     mse_referral_routes, medical_services_routes
from site_app.routes.reports import main_reports_routes
from site_app.models.main_tables import DefectList
from site_app.models.authorization import User, Role, Permission
from site_app.models.reference import Mkb10, RefOtdels, RefDoctors
from site_app.models.main_tables import DefectList, Patients
from site_app.models.medical_services import RefKmu

# from site_app import db
from site_app.models.db_generate import mkb_loader, ref_loader


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'DefectList': DefectList, 'session': db.session, 'Mkb10': Mkb10,
            'mkb_loader': mkb_loader, 'ref_loader': ref_loader, 'Patients': Patients, 'RefOtdels': RefOtdels,
            'RefDoctors': RefDoctors, 'Role': Role, 'Permission': Permission, 'RefKmu': RefKmu}
