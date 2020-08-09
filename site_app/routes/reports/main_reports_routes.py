from site_app import app
from flask_login import login_required
from flask import render_template, send_file


@app.route('/reports/', methods=['GET'])
@login_required
def reports_list():
    return render_template(r'reports/reports_list.html')


@app.route('/reports/smo_expert_defects', methods=['GET'])
@login_required
def smo_expert_defects():
    return send_file(r'files\report.xls',
             as_attachment=True,
             mimetype='application/vnd.ms-excel',
             attachment_filename="дефекты.xlsx")
