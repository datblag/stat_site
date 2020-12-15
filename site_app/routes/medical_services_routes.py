import logging
from flask_login import login_required
from flask import render_template, request, redirect, url_for, session
from site_app import app
from site_app.forms import MedServiceEditForm
from site_app.models.medical_services import MedicalServices, RefKmu
from site_app.models.reference import RefDoctors, Mkb10
from site_app.models.main_tables import Patients
from site_app import db
from site_app.site_config import FLASKY_POSTS_PER_PAGE
from site_app.models.authorization import Permission
from site_app.decorators import permission_required


@app.route('/med_service_edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MEDICAL_SERVICE)
def med_service_edit(service_id=0):
    form = MedServiceEditForm(request.form)

    if service_id == 0:
        pass
    else:
        service_rec = MedicalServices.query.get_or_404(service_id)
    # # print(form.validate_on_submit(), request.method, request)
    if request.method == 'POST' and form.validate_on_submit():
        if service_id == 0:
            service_rec = MedicalServices()
            service_rec.is_deleted = 0
            service_rec.patient = Patients.query.get(session['patient_id'])

        doctor_ref_rec = RefDoctors.query.filter_by(doctor_stat_code=form.doctor_code.data.strip()).first()
        service_rec.doctor_id_ref = doctor_ref_rec.doctor_id

        mkb10_ref_rec = Mkb10.query.filter_by(code=form.disease.data.strip()).first()
        service_rec.disease_id_ref = mkb10_ref_rec.id

        service_rec.service_date = form.service_date.data

        service_rec.kmu_id_ref = int(form.service_ref.data)

        db.session.add(service_rec)
        db.session.commit()
        if 'patient_id' in session:
            return redirect(url_for('patient_open', patient_id=session['patient_id']))
        else:
            return redirect(url_for('med_service_list'))

    if service_id != 0 and service_id is not None and request.method == 'GET':
        if service_rec.doctor_id_ref:
            doctor_ref_rec = RefDoctors.query.get(service_rec.doctor_id_ref)
            if doctor_ref_rec:
                form.doctor_code.data = doctor_ref_rec.doctor_stat_code
            else:
                form.doctor_code.data = ""

        if service_rec.disease_id_ref:
            disease_ref_rec = Mkb10.query.get(service_rec.disease_id_ref)
            if disease_ref_rec:
                form.disease.data = disease_ref_rec.code
            else:
                form.disease.data = ""

        logging.warning(['service_rec.kmu_id_ref', service_rec.kmu_id_ref])
        if service_rec.kmu_id_ref:
            kmu_ref_rec = RefKmu.query.get(service_rec.kmu_id_ref)
            if kmu_ref_rec:
                form.service_ref.data = str(kmu_ref_rec.kmu_id)
            else:
                form.service_ref.data = '0'

        form.service_date.data = service_rec.service_date




        # if mse_rec.disability_group_id_ref:
        #     temp_ref_rec = RefDisabilityGroup.query.get(mse_rec.disability_group_id_ref)
        #     if temp_ref_rec:
        #         form.disability_group_id.data = temp_ref_rec.disability_group_id
        #         form.disability_group_label.data = temp_ref_rec.disability_group_name
        #     else:
        #         form.disability_group_id.data = ""
        #         form.disability_group_label.data = ""
        #
        # if mse_rec.bureau_id_ref:
        #     temp_ref_rec = RefBureauMse.query.get(mse_rec.bureau_id_ref)
        #     if temp_ref_rec:
        #         form.bureau_id.data = temp_ref_rec.bureau_id
        #         form.bureau_label.data = temp_ref_rec.bureau_name
        #     else:
        #         form.bureau_id.data = ""
        #         form.bureau_label.data = ""
        # form.degree_disability.data = mse_rec.degree_disability
        # form.mse_comment.data = mse_rec.mse_comment
        # form.expert_date.data = mse_rec.expert_date
        # form.next_date.data = mse_rec.next_date
        # form.mse_disease.data = mse_rec.mse_disease
        # form.is_first_direction.data = mse_rec.is_first_direction
        #
        # form.is_disability_no_set.data = mse_rec.is_disability_no_set
        # form.is_set_indefinitely.data = mse_rec.is_set_indefinitely

    rows_kmu = RefKmu.query.all()
    kmu_choices = list()
    kmu_choices.append((0, ''))
    for r_kmu in rows_kmu:
        kmu_choices.append((r_kmu.kmu_id, r_kmu.kmu_name.strip() + ' (' + r_kmu.oms_code.strip() + ')'))
    form.service_ref.choices = kmu_choices
    # form.service_ref.data = '2'
    return render_template('documents/med_service/med_service_edit.html', service_id=str(service_id), form=form)


@app.route('/med_service/', methods=['GET'])
@login_required
def med_service_list():
    if 'patient_id' in session:
        session.pop('patient_id', None)
    page = request.args.get('page', 1, type=int)
    pagination = MedicalServices.get_list(MedicalServices).paginate(
        page, per_page=FLASKY_POSTS_PER_PAGE,
        error_out=False)
    services = pagination.items
    # logging.warning(['refferal list', referrals])
    return render_template('documents/med_service/med_service.html', pagination=pagination, services=services)


@app.route('/med_service_close/')
@login_required
def med_service_close():
    if 'patient_id' in session:
        return redirect(url_for('patient_open', patient_id=session['patient_id']))
    else:
        return redirect(url_for('med_service_list'))
