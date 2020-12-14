from site_app import db
from .dbext import DatExtDB


class MedicalServices(db.Model, DatExtDB):
    # выполненные медицинские услуги
    __tablename__ = 'med_services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_date = db.Column(db.Date)
    patient_id_ref = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    is_deleted = db.Column(db.Integer)
    doctor_id_ref = db.Column(db.Integer, db.ForeignKey('ref_doctors.doctor_id'))
    kmu_id_ref = db.Column(db.Integer, db.ForeignKey('ref_kmu.kmu_id'))


class RefKmu(db.Model, DatExtDB):
    # справочник мед услуг
    __tablename__ = 'ref_kmu'
    kmu_id = db.Column(db.Integer, primary_key=True)
    kmu_name = db.Column(db.String(100))
    oms_code = db.Column(db.String(16))
    med_services = db.relationship('MedicalServices', backref='kmu', lazy='dynamic')
