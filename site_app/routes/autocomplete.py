from site_app import db, app
from site_app.models.reference import RefDoctors, RefDefectTypes
from flask import Response
import json


doctors = []
doctor_dbf = db.session.query(RefDoctors).all()
for rec in doctor_dbf:
    doctors.append({'label': rec.doctor_stat_code + " " + rec.doctor_name.strip(), 'value': rec.doctor_stat_code})


defects = []
defect_recs = db.session.query(RefDefectTypes).all()
for rec in defect_recs:
    defects.append({'label': rec.defect_type_code + " " + rec.defect_name.strip(), 'value': rec.defect_type_code})


@app.route('/_autocomplete_doctors', methods=['GET'])
def autocomplete_doctors():
    return Response(json.dumps(doctors), mimetype='application/json')


@app.route('/_autocomplete_defect_types', methods=['GET'])
def autocomplete_defect_types():
    return Response(json.dumps(defects), mimetype='application/json')
