from site_app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Permission:
    EXPERT = 1
    REPORT = 2
    ADMIN = 4
    MEDICAL_SERVICE = 8


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_name = db.Column(db.String(50))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<Пользовательu {}>'.format(self.user_name)

    def set_login(self, login):
        self.user_login = login.lower()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def __repr__(self):
        return '<Пользователь {}>'.format(str(self.id)+' '+self.user_login)


