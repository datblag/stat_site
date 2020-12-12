from site_app import app
from flask import render_template, request, redirect, url_for, session
from site_app.models.main_tables import Patients, DefectList, MseReferral
from flask_login import login_required
from site_app.site_config import FLASKY_POSTS_PER_PAGE
from site_app.forms import AddPatientForm, PatientForm
from site_app.models.mis_db import HltMkabTable, session_mis
from site_app import db


@app.route('/patient_add/', methods=['GET', 'POST'])
@login_required
def patient_add():
    form = AddPatientForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.num.data:
            query = session_mis.query(HltMkabTable)
            query = query.filter(HltMkabTable.num.ilike('%' + form.num.data + '%'))
        else:
            query = session_mis.query(HltMkabTable)
            query = query.filter(HltMkabTable.family.ilike('%'+form.fam.data+'%'))
            query = query.filter(HltMkabTable.name.ilike('%'+form.im.data+'%'))
            query = query.filter(HltMkabTable.ot.ilike('%'+form.ot.data+'%'))
            if form.birthday.data:
                query = query.filter(HltMkabTable.date_bd == form.birthday.data)

        query = query.order_by(HltMkabTable.family, HltMkabTable.name, HltMkabTable.ot)
        return render_template('patientadd.html', form=form, patients=query.limit(100).all())

    return render_template('patientadd.html', form=form)


@app.route('/patient_add/<int:mkabid>', methods=['GET'])
@login_required
def patient_save_from_mis(mkabid=0):
    if mkabid:
        query = session_mis.query(HltMkabTable)
        query = query.filter(HltMkabTable.mkabid == mkabid)
        query = query.limit(1).all()
        if query:
            query_patients = Patients.query.filter(Patients.mis_id == query[0].mkabid).all()
            if not query_patients:
                patient_new_rec = Patients()
                patient_new_rec.fam = query[0].family
                patient_new_rec.im = query[0].name
                patient_new_rec.ot = query[0].ot
                patient_new_rec.birthday = query[0].date_bd
                patient_new_rec.num = query[0].num
                patient_new_rec.mis_id = query[0].mkabid
                patient_new_rec.is_deleted = 0
                db.session.add(patient_new_rec)
                db.session.commit()
                return redirect(url_for('patient_open', patient_id=patient_new_rec.patient_id))

            return redirect(url_for('patient_open', patient_id=query_patients[0].patient_id))


@app.route('/patient_open/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def patient_open(patient_id=0):
    if patient_id:
        patient_rec = Patients.query.get(patient_id)
        if patient_rec is None:
            return redirect(url_for('patients_list'))
        form = PatientForm()
        form.fam.data = patient_rec.fam
        form.im.data = patient_rec.im
        form.ot.data = patient_rec.ot
        form.birthday.data = patient_rec.birthday
        form.num.data = patient_rec.num
        session['patient_id'] = patient_rec.patient_id
        document_list = []
        defect_list = DefectList.get_list(DefectList, patient_id=patient_rec.patient_id).all()
        for rec in defect_list:
            document_list.append({'type': 1, 'typename': 'Экспертиза СМО', 'id': rec.defect_id,
                                  'date': rec.expert_date, 'doctor': rec.doctor.doctor_name})

        mse_list = MseReferral.get_list(MseReferral, patient_id=patient_rec.patient_id).all()
        for rec in mse_list:
            document_list.append({'type': 2, 'typename': 'Направление на МСЭ', 'id': rec.mse_id,
                                  'date': rec.expert_date, 'doctor': rec.doctor.doctor_name})

        document_list.sort(key=lambda dictionary: dictionary['date'])

        return render_template('patientopen.html', form=form, patient=patient_rec, document_list=document_list)
        # return render_template('patientopen.html', form=form, patient=patient_rec,
        #                        defect_list=DefectList.get_list(DefectList, patient_id=patient_rec.patient_id).all(),
        #                        mse_referral=MseReferral.get_list(MseReferral, patient_id=patient_rec.patient_id).all())
    return redirect(url_for('patients_list'))


@app.route('/patients/', methods=['GET'])
@login_required
def patients_list():
    if 'patient_id' in session:
        session.pop('patient_id', None)
    page = request.args.get('page', 1, type=int)
    # Patients.query.filter(Patients.is_deleted != 1)
    pagination = Patients.get_list(Patients).\
        order_by(Patients.fam, Patients.im, Patients.ot).paginate(page, per_page=FLASKY_POSTS_PER_PAGE, error_out=False)

    patients = pagination.items
    return render_template('patients.html', pagination=pagination, patients=patients)
