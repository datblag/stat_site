from site_app import app
from flask_login import login_required
from flask import render_template, send_file
from site_app.template_render import TemplateRender
from site_app.models.main_tables import DefectList
import os
import uuid
import logging


@app.route('/reports/', methods=['GET'])
@login_required
def reports_list():
    return render_template(r'reports/reports_list.html')


@app.route('/reports/smo_expert_defects', methods=['GET'])
@login_required
def smo_expert_defects():
    query = DefectList.query.filter_by(is_deleted=0).all()
    file_name = str(uuid.uuid4())+'.xlsx'
    file_full_name = os.path.join(os.getcwd(), 'site_app', 'files', file_name)
    tr = TemplateRender(16, file_name=file_full_name,
                        copyfile=False, open_in_excel=False, sheet_title='Список')

    tr.add_titles_row([['№ карты', 10], ['Фамилия', 20], ['Имя', 20], ['Отчество', 20], ['ДР', 20],
                       ['Врач', 20], ['Отделение', 20], ['МКБ10', 20], ['Период', 20], ['', 20], ['Код дефекта', 20],
                       ['Описание дефекта', 20], ['Стоимость услуги', 20], ['Не полежит оплате', 20], ['Всего', 20],
                       ['Штраф', 20], ['Дата экспертизы', 20], ['Эксперт', 20], ['Акт', 20]])

    for defect in query:
        logging.warning([defect, defect.doctor])
        tr.add_data_row([[defect.patient.num, defect.patient.fam, defect.patient.im, defect.patient.ot,
                          defect.patient.birthday, defect.doctor.doctor_name, defect.doctor.otdel.otdel_name,
                          defect.disease, defect.period_begin, defect.period_end, defect.error_list,
                          defect.error_comment, defect.sum_service, defect.sum_no_pay, defect.get_sum_total(),
                          defect.sum_penalty, defect.expert_date, defect.expert_name, defect.expert_act_number]])

    tr.close_template_file()
    return send_file(os.path.join('files', file_name), as_attachment=True, mimetype='application/vnd.ms-excel',
                     attachment_filename="дефекты.xlsx")
