from site_app import app, db
from flask import render_template, request, redirect, url_for, session
from site_app.forms import DefectEditForm, DefectDeleteForm
from site_app.models.main_tables import Patients, DefectList
from flask_login import login_required
from site_app.models.reference import RefDoctors
from site_app.models.authorization import Permission
from site_app.site_config import FLASKY_POSTS_PER_PAGE
import datetime
import logging
from site_app.decorators import admin_required, permission_required


@app.route('/defect/', methods=['GET'])
@login_required
@permission_required(Permission.EXPERT)
def defect_list():
    if 'patient_id' in session:
        session.pop('patient_id', None)
    page = request.args.get('page', 1, type=int)
    pagination = DefectList.get_list(DefectList).paginate(
        page, per_page=FLASKY_POSTS_PER_PAGE,
        error_out=False)
    defects = pagination.items
    return render_template('documents/smo_defect/defect.html', pagination=pagination, defects=defects)


@login_required
@app.route('/defect_close/')
def defect_close():
    if 'patient_id' in session:
        return redirect(url_for('patient_open', patient_id=session['patient_id']))
    else:
        return redirect(url_for('defect_list'))


@app.route('/defect/<int:defectid>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EXPERT)
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
            defect_rec.is_deleted = 0
            defect_rec.patient = Patients.query.get(session['patient_id'])

        doctor_ref_rec = RefDoctors.query.filter_by(doctor_stat_code=form.doctor_code.data.strip()).first()
        defect_rec.doctor_id_ref = doctor_ref_rec.doctor_id

        defect_rec.expert_date = form.expert_date.data
        defect_rec.expert_name = form.expert_name.data
        defect_rec.expert_act_number = form.expert_act_number.data
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
        logging.warning(form.expert_date.data)
        session['expert_date'] = form.expert_date.data.strftime('%Y-%m-%d')
        session['expert_name'] = form.expert_name.data
        session['expert_act_number'] = form.expert_act_number.data

        if 'patient_id' in session:
            return redirect(url_for('patient_open', patient_id=session['patient_id']))
        else:
            return redirect(url_for('defect_list'))

    if defectid != 0 and defectid is not None and request.method == 'GET':
        if defect_rec.doctor_id_ref:
            doctor_ref_rec = RefDoctors.query.get(defect_rec.doctor_id_ref)
            if doctor_ref_rec:
                form.doctor_code.data = doctor_ref_rec.doctor_stat_code
            else:
                form.doctor_code.data = ""

        form.defect_codes.data = defect_rec.error_list
        form.defect_comment.data = defect_rec.error_comment
        form.expert_date.data = defect_rec.expert_date
        form.expert_name.data = defect_rec.expert_name
        form.expert_act_number.data = defect_rec.expert_act_number

        form.disease.data = defect_rec.disease

        form.period_start.data = defect_rec.period_begin
        form.period_end.data = defect_rec.period_end

        form.sum_service.data = defect_rec.sum_service
        form.sum_no_pay.data = defect_rec.sum_no_pay
        form.sum_penalty.data = defect_rec.sum_penalty
    else:
        if 'expert_act_number' in session:
            form.expert_act_number.data = session['expert_act_number']
        if 'expert_name' in session:
            form.expert_name.data = session['expert_name']
        if 'expert_date' in session:
            logging.warning(session['expert_date'])
            form.expert_date.data = datetime.datetime.strptime(session['expert_date'], '%Y-%m-%d')

    return render_template('documents/smo_defect/defectedit.html', defectid=str(defectid), form=form)


@app.route('/defect_delete/<int:defectid>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EXPERT)
def defect_delete(defectid=0):
    form = DefectDeleteForm(request.form)
    if defectid == 0 or defectid is None:
        if 'patient_id' in session:
            return redirect(url_for('patient_open', patient_id=session['patient_id']))
        else:
            return redirect(url_for('defect_list'))
    if request.method == 'POST' and form.validate_on_submit():
        d = DefectList.query.filter_by(defect_id=defectid).first()
        logging.warning(['delete defect', defectid])
        d.is_deleted = 1
        db.session.add(d)
        db.session.commit()
        if 'patient_id' in session:
            return redirect(url_for('patient_open', patient_id=session['patient_id']))
        else:
            return redirect(url_for('defect_list'))
    return render_template('delete_record_answer.html', record_id=str(defectid), form=form)
