from site_app import db
from .main_tables import DefectList, MseReferral
from .medical_services import MedicalServices


class Mkb10(db.Model):
    # диагнозы
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
    med_services = db.relationship('MedicalServices', backref='disease', lazy='dynamic')

    def __repr__(self):
        return '<{}{}>'.format(self.code, self.name)


class RefDoctors(db.Model):
    # врачи
    __tablename__ = 'ref_doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    doctor_stat_code = db.Column(db.String(4))
    doctor_name = db.Column(db.String(35))
    defects = db.relationship('DefectList', backref='doctor', lazy='dynamic')
    mse_referral = db.relationship('MseReferral', backref='doctor', lazy='dynamic')
    med_services = db.relationship('MedicalServices', backref='doctor', lazy='dynamic')
    otdel_id_ref = db.Column(db.Integer, db.ForeignKey('ref_otdels.otdel_id'))

    def __repr__(self):
        return '<Врач {}>'.format(self.doctor_stat_code+' '+self.doctor_name)


class RefOtdels(db.Model):
    # отделения
    __tablename__ = 'ref_otdels'
    otdel_id = db.Column(db.Integer, primary_key=True)
    otdel_stat_code = db.Column(db.String(2))
    otdel_name = db.Column(db.String(50))
    doctors = db.relationship('RefDoctors', backref='otdel', lazy='dynamic')

    def __repr__(self):
        return 'Отделение: {}'.format(self.otdel_name)


class RefDefectTypes(db.Model):
    # дефекты экспертизы смо
    __tablename__ = 'ref_defect_types'
    defect_type_id = db.Column(db.Integer, primary_key=True)
    defect_type_code = db.Column(db.String(6))
    defect_name = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, nullable=True)


class RefBureauMse(db.Model):
    # бюро мсэ
    __tablename__ = 'ref_bureau_mse'
    bureau_id = db.Column(db.Integer, primary_key=True)
    bureau_name = db.Column(db.String(15))
    mse_referral = db.relationship('MseReferral', backref='bureau', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.bureau_name)


class RefDisabilityGroup(db.Model):
    # группа инвалидности
    __tablename__ = 'ref_disability_group'
    disability_group_id = db.Column(db.Integer, primary_key=True)
    disability_group_name = db.Column(db.String(15))
    mse_referral = db.relationship('MseReferral', backref='disability_group', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.disability_group_name)


