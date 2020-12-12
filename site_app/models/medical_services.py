from site_app import db
from .main_tables import DatExtDB


class MedicalServices(db.Model, DatExtDB):
    # выполненные медицинские услуги
    __tablename__ = 'med_services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_date = db.Column(db.Date)
    patient_id_ref = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
