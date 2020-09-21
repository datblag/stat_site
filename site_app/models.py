from site_app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Patients(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    fam = db.Column(db.String(40))
    im = db.Column(db.String(40))
    ot = db.Column(db.String(40))
    birthday = db.Column(db.Date)
    num = db.Column(db.String(40))
    mis_id = db.Column(db.Integer)
    is_deleted = db.Column(db.Integer)
    defects_smo_expert = db.relationship('DefectList', backref='patient', lazy='dynamic')

    def __repr__(self):
        return '{} {} {} {}'.format(self.fam, self.im, self.ot, datetime.datetime.strftime(self.birthday, '%d.%m.%Y'))


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


class Permission:
    EXPERT = 1
    REPORT = 2
    ADMIN = 4


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(6), unique=True)
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


class RefDoctors(db.Model):
    __tablename__ = 'ref_doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    doctor_stat_code = db.Column(db.String(4))
    doctor_name = db.Column(db.String(50))
    defects = db.relationship('DefectList', backref='doctor', lazy='dynamic')
    # otdel_id_ref = db.Column(db.Integer)
    otdel_id_ref = db.Column(db.Integer, db.ForeignKey('ref_otdels.otdel_id'))

    def __repr__(self):
        return '<Врач {}>'.format(self.doctor_stat_code+' '+self.doctor_name)


class RefOtdels(db.Model):
    __tablename__ = 'ref_otdels'
    otdel_id = db.Column(db.Integer, primary_key=True)
    otdel_stat_code = db.Column(db.String(2))
    otdel_name = db.Column(db.String(50))
    doctors = db.relationship('RefDoctors', backref='otdel', lazy='dynamic')

    def __repr__(self):
        return 'Отделение: {}'.format(self.otdel_name)



class DatExtDB:
    def get_list(self, patient_id=None, order=None):
        query = self.query.filter_by(is_deleted=0).order_by(order)
        if patient_id is not None:
            query = query.filter_by(patient_id_ref=patient_id)
        return query


class DefectList(db.Model, DatExtDB):
    __tablename__ = 'defect_list'
    defect_id = db.Column(db.Integer, primary_key=True)
    doctor_id_ref = db.Column(db.Integer, db.ForeignKey('ref_doctors.doctor_id'))
    patient_id_ref = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    error_list = db.Column(db.String(50))
    error_comment = db.Column(db.String(250))
    period_begin = db.Column(db.Date)
    period_end = db.Column(db.Date)
    disease = db.Column(db.String(5))
    sum_service = db.Column(db.Numeric(15, 2))
    sum_no_pay = db.Column(db.Numeric(15, 2))
    sum_penalty = db.Column(db.Numeric(15, 2))
    is_deleted = db.Column(db.Integer)
    expert_date = db.Column(db.Date)
    expert_name = db.Column(db.String(40))
    expert_act_number = db.Column(db.String(40))

    # def get_list(self, patient_id=None):
    #     query = self.query.filter_by(is_deleted=0)
    #     if patient_id is not None:
    #         query = query.filter_by(patient_id_ref=patient_id)
    #     print(patient_id, query)
    #     return query.order_by(DefectList.defect_id.desc())

    def get_sum_total(self):
        return self.sum_service-self.sum_no_pay-self.sum_penalty

class RefDefectTypes(db.Model):
    __tablename__ = 'ref_defect_types'
    defect_type_id = db.Column(db.Integer, primary_key=True)
    defect_type_code = db.Column(db.String(6))
    defect_name = db.Column(db.String(500))
