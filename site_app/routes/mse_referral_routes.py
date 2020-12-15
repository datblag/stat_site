from site_app import app, db
from flask import render_template, request, redirect, url_for, session
from site_app.forms import MseReferralEditForm, DefectDeleteForm
from site_app.models.main_tables import MseReferral, Patients
from flask_login import login_required
from site_app.models.reference import RefDoctors, RefDisabilityGroup, RefBureauMse
from site_app.models.authorization import Permission
from site_app.site_config import FLASKY_POSTS_PER_PAGE
import datetime
import logging
from site_app.decorators import admin_required, permission_required


@app.route('/mse_ref/<int:mse_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EXPERT)
def mse_referral_edit(mse_id=0):
    form = MseReferralEditForm(request.form)
    if mse_id == 0:
        pass
    else:
        mse_rec = MseReferral.query.get_or_404(mse_id)
    # # print(form.validate_on_submit(), request.method, request)
    if request.method == 'POST' and form.validate_on_submit():
        if mse_id == 0:
            mse_rec = MseReferral()
            mse_rec.is_deleted = 0
            mse_rec.degree_disability = 0
            mse_rec.patient = Patients.query.get(session['patient_id'])

        doctor_ref_rec = RefDoctors.query.filter_by(doctor_stat_code=form.doctor_code.data.strip()).first()
        mse_rec.doctor_id_ref = doctor_ref_rec.doctor_id

        disability_group_rec = RefDisabilityGroup.query.get(form.disability_group_id.data.strip())
        if disability_group_rec is not None:
            mse_rec.disability_group_id_ref = disability_group_rec.disability_group_id
        else:
            mse_rec.disability_group_id_ref = None
        mse_rec.bureau_id_ref = RefBureauMse.query.get(form.bureau_id.data.strip()).bureau_id

        mse_rec.is_first_direction = 0

        if form.is_first_direction.data:
            mse_rec.is_first_direction = 1

        mse_rec.is_disability_no_set = 0
        if form.is_disability_no_set.data:
            mse_rec.is_disability_no_set = 1

        mse_rec.degree_disability = form.degree_disability.data

        mse_rec.is_set_indefinitely = 0
        if form.is_set_indefinitely.data:
            mse_rec.is_set_indefinitely = 1

        mse_rec.expert_date = form.expert_date.data
        mse_rec.next_date = form.next_date.data
        mse_rec.mse_comment = form.mse_comment.data
        mse_rec.mse_disease = form.mse_disease.data
        db.session.add(mse_rec)
        db.session.commit()
        if 'patient_id' in session:
            return redirect(url_for('patient_open', patient_id=session['patient_id']))
        else:
            return redirect(url_for('mse_referral_list'))
    #
    if mse_id != 0 and mse_id is not None and request.method == 'GET':
        if mse_rec.doctor_id_ref:
            doctor_ref_rec = RefDoctors.query.get(mse_rec.doctor_id_ref)
            if doctor_ref_rec:
                form.doctor_code.data = doctor_ref_rec.doctor_stat_code
            else:
                form.doctor_code.data = ""

        if mse_rec.disability_group_id_ref:
            temp_ref_rec = RefDisabilityGroup.query.get(mse_rec.disability_group_id_ref)
            if temp_ref_rec:
                form.disability_group_id.data = temp_ref_rec.disability_group_id
                form.disability_group_label.data = temp_ref_rec.disability_group_name
            else:
                form.disability_group_id.data = ""
                form.disability_group_label.data = ""

        if mse_rec.bureau_id_ref:
            temp_ref_rec = RefBureauMse.query.get(mse_rec.bureau_id_ref)
            if temp_ref_rec:
                form.bureau_id.data = temp_ref_rec.bureau_id
                form.bureau_label.data = temp_ref_rec.bureau_name
            else:
                form.bureau_id.data = ""
                form.bureau_label.data = ""
        form.degree_disability.data = mse_rec.degree_disability
        form.mse_comment.data = mse_rec.mse_comment
        form.expert_date.data = mse_rec.expert_date
        form.next_date.data = mse_rec.next_date
        form.mse_disease.data = mse_rec.mse_disease
        form.is_first_direction.data = mse_rec.is_first_direction

        form.is_disability_no_set.data = mse_rec.is_disability_no_set
        form.is_set_indefinitely.data = mse_rec.is_set_indefinitely
    return render_template('documents/mse_referral/mse_referral_edit.html', mse_id=str(mse_id), form=form)


@app.route('/mse_ref/', methods=['GET'])
@login_required
@permission_required(Permission.EXPERT)
def mse_referral_list():
    if 'patient_id' in session:
        session.pop('patient_id', None)
    page = request.args.get('page', 1, type=int)
    pagination = MseReferral.get_list(MseReferral).paginate(
        page, per_page=FLASKY_POSTS_PER_PAGE,
        error_out=False)
    referrals = pagination.items
    logging.warning(['refferal list', referrals])
    return render_template('documents/mse_referral/mse_referral.html', pagination=pagination, referrals=referrals)


@app.route('/mse_ref_close/')
@login_required
def mse_referral_close():
    if 'patient_id' in session:
        return redirect(url_for('patient_open', patient_id=session['patient_id']))
    else:
        return redirect(url_for('mse_referral_list'))


@app.route('/mse_ref_delete/<int:mse_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.EXPERT)
def mse_referral_delete(mse_id=0):
    form = DefectDeleteForm(request.form)
    if mse_id == 0 or mse_id is None:
        if 'patient_id' in session:
            return redirect(url_for('patient_open', patient_id=session['patient_id']))
        else:
            return redirect(url_for('mse_referral_list'))
    if request.method == 'POST' and form.validate_on_submit():
        d = MseReferral.query.filter_by(mse_id=mse_id).first()
        logging.warning(['delete mse referral', mse_id])
        d.is_deleted = 1
        db.session.add(d)
        db.session.commit()
        if 'patient_id' in session:
            return redirect(url_for('patient_open', patient_id=session['patient_id']))
        else:
            return redirect(url_for('mse_referral_list'))
    return render_template('delete_record_answer.html', record_id=str(mse_id), form=form)

