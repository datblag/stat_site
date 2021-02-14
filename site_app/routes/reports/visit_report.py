from site_app import app
import logging
import datetime
from flask import render_template, send_file, request
from site_app.forms import PeriodForm
from site_app.reports.cases import rep_case
import os

@app.route('/reports/case', methods=['GET', 'POST'])
def report_case():
    form = PeriodForm()
    if request.method == 'POST' and form.validate_on_submit():

        prm_date_end_rep = form.end_date.data + datetime.timedelta(days=1)
        logging.warning(type(form.begin_date.data))
        logging.warning(form.begin_date.data)
        logging.warning(prm_date_end_rep)

        file_name = rep_case(prm_date_start=form.begin_date.data.strftime('%Y-%m-%d'), prm_date_end=form.end_date.data.strftime('%Y-%m-%d'))

        return send_file(os.path.join('files', file_name), as_attachment=True, mimetype='application/vnd.ms-excel',
                         attachment_filename="случаи.xlsx")
    return render_template(r'reports/report_period.html', form=form)
