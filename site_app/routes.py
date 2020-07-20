from site_app import app, db
from flask import render_template, Response, request, redirect, url_for, flash
from site_app.models import DefectList
from site_app.site_config import STAT_PATH
from site_app.forms import DefectEditForm
import dbf
import os
import json
from site_app.models import DefectList, RefDoctors, RefDefectTypes


doctors = []
doctor_dbf = db.session.query(RefDoctors).all()
for rec in doctor_dbf:
    doctors.append({'label': rec.doctor_stat_code + " " + rec.doctor_name.strip(), 'value': rec.doctor_stat_code})


defects = []
defect_recs = db.session.query(RefDefectTypes).all()
for rec in defect_recs:
    defects.append({'label': rec.defect_type_code + " " + rec.defect_name.strip(), 'value': rec.defect_type_code})


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/defect/', methods=['GET'])
def defect_list():

    defects = DefectList.query.all()
    return render_template('defect.html', defects=defects)


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    print(doctors)
    return Response(json.dumps(doctors), mimetype='application/json')


@app.route('/_autocomplete2', methods=['GET'])
def autocomplete2():
    print(defects)
    return Response(json.dumps(defects), mimetype='application/json')


@app.route('/defect/<int:defectid>', methods=['GET', 'POST'])
def defect_edit(defectid=0):
    form = DefectEditForm(request.form)
    if defectid == 0:
        pass
    else:
        defect_rec = DefectList.query.get_or_404(defectid)
    # print(form.validate_on_submit(), request.method, request)
    if request.method == 'POST' and form.validate_on_submit():
        if defectid == 0:
            defect_rec = DefectList()
        defect_rec.history = form.history.data

        doctor_ref_rec = RefDoctors.query.filter_by(doctor_stat_code=form.doctor_code.data.strip()).first()
        defect_rec.doctor_id_ref = doctor_ref_rec.doctor_id

        defect_rec.error_list = form.defect_codes.data
        defect_rec.error_comment = form.defect_comment.data

        defect_rec.disease = form.disease.data

        defect_rec.period_begin = form.period_start.data
        defect_rec.period_end = form.period_end.data

        defect_rec.sum_service = form.sum_service.data
        defect_rec.sum_no_pay = form.sum_no_pay.data
        defect_rec.sum_penalty = form.sum_penalty.data

        db.session.add(defect_rec)
        db.session.commit()
        return redirect(url_for('defect_list'))

    if defectid != 0:
        form.history.data = defect_rec.history

        if defect_rec.doctor_id_ref:
            doctor_ref_rec = RefDoctors.query.get(defect_rec.doctor_id_ref)
            if doctor_ref_rec:
                form.doctor_code.data = doctor_ref_rec.doctor_stat_code
            else:
                form.doctor_code.data = ""

        form.defect_codes.data = defect_rec.error_list
        form.defect_comment.data = defect_rec.error_comment

        form.disease.data = defect_rec.disease

        form.period_start.data = defect_rec.period_begin
        form.period_end.data = defect_rec.period_end

        print(defect_rec.sum_service)

        form.sum_service.data = defect_rec.sum_service
        form.sum_no_pay.data = defect_rec.sum_no_pay
        form.sum_penalty.data = defect_rec.sum_penalty

    return render_template('defectedit.html', defectid=str(defectid), form=form)


@app.route('/doctor/', methods=['GET'])
def doctor_list():
    # doctor_dbf = dbf.Table(os.path.join(STAT_PATH, 'doctor.dbf'))
    # doctor_dbf.open()
    # # index_doctor=doctor_dbf.create_index(lambda rec: (rec.scode.strip()))
    # doctor_dbf.first_record
    # for rec in doctor_dbf:
    #     doctor_recs = db.session.query(RefDoctors).filter_by(doctor_stat_code=rec["SCODE"]).all()
    #     if not doctor_recs:
    #         doctor_rec = RefDoctors(doctor_stat_code=rec["SCODE"], doctor_name=rec["NAME"].strip())
    #         db.session.add(doctor_rec)
    #         db.session.commit()
    #     print(doctor_recs)
    #
    # print("ALL")
    # doctor_dbf.close()
    # # print(cities)
    doctors = db.session.query(RefDoctors).all()
    return render_template('doctor.html', doctors=doctors)

