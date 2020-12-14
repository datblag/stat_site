import logging
from flask_login import login_required
from flask import render_template, request, redirect, url_for, session
from site_app import app
from site_app.forms import MedServiceEditForm
from site_app.models.medical_services import MedicalServices


@app.route('/med_service_edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def med_service_edit(service_id=0):
    form = MedServiceEditForm(request.form)
    if service_id == 0:
        pass
    else:
        mse_rec = MedicalServices.query.get_or_404(service_id)
    # # print(form.validate_on_submit(), request.method, request)
    if request.method == 'POST' and form.validate_on_submit():
        logging.warning(['Мед услуга', form.service_ref.data])
        return ''

    form.service_ref.choices = ['5', '6', '7']
    return render_template('documents/med_service/med_service_edit.html', service_id=str(service_id), form=form)
