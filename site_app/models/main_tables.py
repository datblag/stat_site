from site_app import db
import datetime


class DatExtDB:
    def get_list(self, patient_id=None, order=None):
        query = self.query.filter(self.is_deleted != 1).order_by(order)
        if patient_id is not None:
            query = query.filter_by(patient_id_ref=patient_id)
        return query


class Patients(db.Model, DatExtDB):
    # пациенты
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
    mse_referral = db.relationship('MseReferral', backref='patient', lazy='dynamic')

    def get_age(self):
        today = datetime.date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def __repr__(self):
        return '{} {} {} {}'.format(self.fam, self.im, self.ot, datetime.datetime.strftime(self.birthday, '%d.%m.%Y'))


class MseReferral(db.Model, DatExtDB):
    # направление на МСЭ
    __tablename__ = 'mse_referral'
    mse_id = db.Column(db.Integer, primary_key=True)
    doctor_id_ref = db.Column(db.Integer, db.ForeignKey('ref_doctors.doctor_id'))
    patient_id_ref = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    # mse_id_ref = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))


class DefectList(db.Model, DatExtDB):
    # дефекты экспертизы страховой компании
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

