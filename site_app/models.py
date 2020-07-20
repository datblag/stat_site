from site_app import db


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




class RefDefectTypes(db.Model):
    __tablename__ = 'ref_defect_types'
    defect_type_id = db.Column(db.Integer, primary_key=True)
    defect_type_code = db.Column(db.String(6))
    defect_name = db.Column(db.String(500))
