from site_app import app, db
from flask import render_template, request, redirect, url_for, session
from site_app.forms import MseReferralEditForm, DefectDeleteForm
from site_app.models.main_tables import MseReferral, Patients
from flask_login import login_required
from site_app.models.reference import RefDoctors
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
            mse_rec.patient = Patients.query.get(session['patient_id'])

        doctor_ref_rec = RefDoctors.query.filter_by(doctor_stat_code=form.doctor_code.data.strip()).first()
        mse_rec.doctor_id_ref = doctor_ref_rec.doctor_id
    #
    #     defect_rec.expert_date = form.expert_date.data
    #     defect_rec.expert_name = form.expert_name.data
    #     defect_rec.expert_act_number = form.expert_act_number.data
    #     defect_rec.error_list = form.defect_codes.data
    #     defect_rec.error_comment = form.defect_comment.data
    #
        mse_rec.mse_disease = form.mse_disease.data
    #
    #     defect_rec.period_begin = form.period_start.data
    #     defect_rec.period_end = form.period_end.data
    #
    #     defect_rec.sum_service = form.sum_service.data
    #     defect_rec.sum_no_pay = form.sum_no_pay.data
    #     defect_rec.sum_penalty = form.sum_penalty.data
    #
        db.session.add(mse_rec)
        db.session.commit()
    #     session['expert_date'] = form.expert_date.data.strftime('%Y-%m-%d')
    #     session['expert_name'] = form.expert_name.data
    #     session['expert_act_number'] = form.expert_act_number.data
    #
        if 'patient_id' in session:
            return redirect(url_for('patient_open', patient_id=session['patient_id']))
        else:
            return redirect(url_for('mse_referral_list'))
    #
    if mse_id != 0 and mse_id is not None:
        if mse_rec.doctor_id_ref:
            doctor_ref_rec = RefDoctors.query.get(mse_rec.doctor_id_ref)
            if doctor_ref_rec:
                form.doctor_code.data = doctor_ref_rec.doctor_stat_code
            else:
                form.doctor_code.data = ""
    #
    #     form.defect_codes.data = defect_rec.error_list
    #     form.defect_comment.data = defect_rec.error_comment
    #     form.expert_date.data = defect_rec.expert_date
    #     form.expert_name.data = defect_rec.expert_name
    #     form.expert_act_number.data = defect_rec.expert_act_number
    #
            form.mse_disease.data = mse_rec.mse_disease
    #
    #     form.period_start.data = defect_rec.period_begin
    #     form.period_end.data = defect_rec.period_end
    #
    #     form.sum_service.data = defect_rec.sum_service
    #     form.sum_no_pay.data = defect_rec.sum_no_pay
    #     form.sum_penalty.data = defect_rec.sum_penalty
    # else:
    #     if 'expert_act_number' in session:
    #         form.expert_act_number.data = session['expert_act_number']
    #     if 'expert_name' in session:
    #         form.expert_name.data = session['expert_name']
    #     if 'expert_date' in session:
    #         logging.warning(session['expert_date'])
    #         form.expert_date.data = datetime.datetime.strptime(session['expert_date'], '%Y-%m-%d')
    #
    return render_template('documnets/mse_referral/mse_referral_edit.html', mse_id=str(mse_id), form=form)


@app.route('/mse_ref/', methods=['GET'])
@login_required
def mse_referral_list():
    if 'patient_id' in session:
        session.pop('patient_id', None)
    page = request.args.get('page', 1, type=int)
    pagination = MseReferral.get_list(MseReferral).paginate(
        page, per_page=FLASKY_POSTS_PER_PAGE,
        error_out=False)
    referrals = pagination.items
    logging.warning(['refferal list', referrals])
    return render_template('documnets/mse_referral/mse_referral.html', pagination=pagination, referrals=referrals)


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

