from site_app import app
from flask import render_template, request, redirect, url_for
from site_app.models import Patients
from flask_login import login_required
from site_app.site_config import FLASKY_POSTS_PER_PAGE
from site_app.forms import AddPatientForm
from site_app.mis_db import HltMkab, session_mis
from site_app import db


@app.route('/patient_add/', methods=['GET', 'POST'])
@login_required
def patient_add():
    form = AddPatientForm()
    if request.method == 'POST' and form.validate_on_submit():
        query = session_mis.query(HltMkab)
        query = query.filter(HltMkab.family.ilike('%'+form.fam.data+'%'))
        query = query.filter(HltMkab.name.ilike('%'+form.im.data+'%'))
        query = query.filter(HltMkab.ot.ilike('%'+form.ot.data+'%'))
        if form.birthday.data:
            query = query.filter(HltMkab.date_bd == form.birthday.data)

        query = query.order_by(HltMkab.family, HltMkab.name, HltMkab.ot)
        return render_template('patientadd.html', form=form, patients=query.limit(100).all())

    return render_template('patientadd.html', form=form)


@app.route('/patient_add/<int:mkabid>', methods=['GET'])
@login_required
def patient_save_from_mis(mkabid=0):
    if mkabid:
        query = session_mis.query(HltMkab)
        query = query.filter(HltMkab.mkabid==mkabid)
        query = query.limit(1).all()
        if query:
            if not Patients.query.filter(Patients.mis_id == query[0].mkabid).all():
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
            return redirect(url_for('patients_list'))


@app.route('/patients/', methods=['GET'])
@login_required
def patients_list():
    page = request.args.get('page', 1, type=int)
    print(page)
    pagination = Patients.query.filter(Patients.is_deleted != 1).\
        order_by(Patients.fam, Patients.im, Patients.ot).paginate(page, per_page=FLASKY_POSTS_PER_PAGE, error_out=False)

    patients = pagination.items
    return render_template('patients.html', pagination=pagination, patients=patients)
