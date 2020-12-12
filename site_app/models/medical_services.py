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
