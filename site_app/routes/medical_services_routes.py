import logging
from flask_login import login_required
from flask import render_template, request, redirect, url_for, session
from site_app import app
from site_app.forms import MedServiceEditForm
from site_app.models.medical_services import MedicalServices, RefKmu
from site_app.models.reference import RefDoctors, Mkb10
from site_app.models.main_tables import Patients
from site_app import db


@app.route('/med_service_edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
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

    rows_kmu = RefKmu.query.all()
    kmu_choices = list()
    kmu_choices.append((0, ''))
    for r_kmu in rows_kmu:
        kmu_choices.append((r_kmu.kmu_id, r_kmu.kmu_name.strip() + ' (' + r_kmu.oms_code.strip() + ')'))

    form.service_ref.choices = kmu_choices
    return render_template('documents/med_service/med_service_edit.html', service_id=str(service_id), form=form)


@app.route('/med_service_close/')
@login_required
def med_service_close():
    if 'patient_id' in session:
        return redirect(url_for('patient_open', patient_id=session['patient_id']))
    else:
        return redirect(url_for('med_service_list'))
