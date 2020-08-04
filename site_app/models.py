from site_app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Mkb10(db.Model):
    __tablename__ = 'mkb10'
    rec_code = db.Column(db.String(9))
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6))
    name = db.Column(db.Text, nullable=False)
    parent_code = db.Column(db.Integer, db.ForeignKey('mkb10.id'), index=True)
    parent = db.relationship(lambda: Mkb10, remote_side=id, backref='sub_mkb10')
    addl_code = db.Column(db.Integer)
    actual = db.Column(db.Boolean)
    date = db.Column(db.Date)
    def __repr__(self):
        return '<{}{}>'.format(self.code, self.name)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_name = db.Column(db.String(50))

    def __repr__(self):
        return '<Пользовательu {}>'.format(self.user_name)

    def set_login(self, login):
        self.user_login = login.lower()


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class RefDoctors(db.Model):
    __tablename__ = 'ref_doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    doctor_stat_code = db.Column(db.String(4))
    doctor_name = db.Column(db.String(500))
    defects = db.relationship('DefectList', backref='doctor', lazy='dynamic')

    def __repr__(self):
        return '<Врач {}>'.format(self.doctor_stat_code+' '+self.doctor_name)


class DefectList(db.Model):
    __tablename__ = 'defect_list'
    defect_id = db.Column(db.Integer, primary_key=True)
    history = db.Column(db.String(6))
    doctor_id_ref = db.Column(db.Integer, db.ForeignKey('ref_doctors.doctor_id'))
    error_list = db.Column(db.String(50))
    error_comment = db.Column(db.String(250))
    period_begin = db.Column(db.Date)
    period_end = db.Column(db.Date)
    disease = db.Column(db.String(5))
    sum_service = db.Column(db.Numeric(15, 2))
    sum_no_pay = db.Column(db.Numeric(15, 2))
    sum_penalty = db.Column(db.Numeric(15, 2))
    is_deleted = db.Column(db.Integer)


class RefDefectTypes(db.Model):
    __tablename__ = 'ref_defect_types'
    defect_type_id = db.Column(db.Integer, primary_key=True)
    defect_type_code = db.Column(db.String(6))
    defect_name = db.Column(db.String(500))
