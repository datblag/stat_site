from site_app import app
from flask_login import login_required
from flask import render_template, send_file, request
from site_app.template_render import TemplateRender
from site_app.models.main_tables import DefectList, MseReferral
from site_app.models.authorization import Permission
from site_app.forms import PeriodForm
import os
import uuid
import logging
import datetime
import psycopg2
from site_app.site_config import sql_pg_eln
from site_app.decorators import permission_required

@app.route('/reports/', methods=['GET'])
@login_required
def reports_list():
    return ''


@app.route('/reports/eln', methods=['GET', 'POST'])
def report_eln():
    form = PeriodForm()
    if request.method == 'POST' and form.validate_on_submit():
        tr = None

        # prm_date_end_rep = (datetime.datetime.strptime(form.begin_date.data, '%Y-%m-%d') +
        #                     datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        prm_date_end_rep = form.end_date.data + datetime.timedelta(days=1)
        logging.warning(type(form.begin_date.data))
        logging.warning(form.begin_date.data)
        logging.warning(prm_date_end_rep)

        file_name = str(uuid.uuid4()) + '.xlsx'
        file_full_name = os.path.join(os.getcwd(), 'site_app', 'files', file_name)
        tr = TemplateRender(3, file_name=file_full_name,
                            copyfile=False, open_in_excel=False, sheet_title='Количество ЭЛН')

        tr.add_header_row(
            'За период с ' + form.begin_date.data.strftime('%d.%m.%Y') +
            ' по ' + form.end_date.data.strftime('%d.%m.%Y'))
        tr.add_header_row('')

        res_str = 'Выписано ЭЛН'
        res_count = 0

        try:
            conn = psycopg2.connect(sql_pg_eln)
        except psycopg2.Error as err:
            res_str = "Connection error: {}".format(err)

        prm_date_start = "'" + form.begin_date.data.strftime('%d.%m.%Y') + "'"
        prm_date_end_rep = "'" + prm_date_end_rep.strftime('%d.%m.%Y') + "'"

        sql = f'SELECT ln_date FROM public.fc_eln_data_history where (ln_date>={prm_date_start}) and (ln_date<{prm_date_end_rep})' \
            f' order by ln_date desc'
        logging.warning(sql)
        try:
            cur = conn.cursor()
            cur.execute(sql)
            data = cur.fetchall()
            res_count = len(data)
        except psycopg2.Error as err:
            res_str = "Query error: {}".format(err)

        tr.add_titles_row([['', 20], ['', 8]])
        tr.current_line -= 1
        tr.add_data_row([[res_str, res_count]])
        tr.close_template_file()

        return send_file(os.path.join('files', file_name), as_attachment=True, mimetype='application/vnd.ms-excel',
                         attachment_filename="выписано элн.xlsx")
    return render_template(r'reports/eln_count.html', form=form)


@app.route('/reports/mse_referral', methods=['GET'])
@login_required
@permission_required(Permission.EXPERT)
def report_mse_referral():
    query = MseReferral.query.filter_by(is_deleted=0).all()
    file_name = str(uuid.uuid4())+'.xlsx'
    file_full_name = os.path.join(os.getcwd(), 'site_app', 'files', file_name)
    tr = TemplateRender(25, file_name=file_full_name,
                        copyfile=False, open_in_excel=False, sheet_title='Список')
    tr.add_titles_row([['№ карты', 10], ['Фамилия', 20], ['Имя', 20], ['Отчество', 20], ['ДР', 20], ['Бюро МСЭ', 20],
                       ['Установлена впервые', 20], ['Не устанволена', 20], ['Бессрочно', 20], ['Дата явки', 20],
                       ['% потери трудоспособности', 20], ['Группа', 20], ['Диагноз', 20], ['Врач', 20],
                       ['Дата экспертизы', 20], ['Примечание', 70]])
    for referral in query:
        tr.add_data_row([[referral.patient.num, referral.patient.fam, referral.patient.im, referral.patient.ot,
                          referral.patient.birthday, str(referral.bureau), referral.is_first_direction,
                          referral.is_disability_no_set, referral.is_set_indefinitely, referral.next_date,
                          referral.degree_disability,
                          str(referral.disability_group) if referral.disability_group is not None else '',
                          referral.mse_disease, str(referral.doctor), referral.expert_date, referral.mse_comment]])
    tr.close_template_file()
    return send_file(os.path.join('files', file_name), as_attachment=True, mimetype='application/vnd.ms-excel',
                     attachment_filename="направления на мсэ.xlsx")


@app.route('/reports/smo_expert_defects', methods=['GET'])
@login_required
@permission_required(Permission.EXPERT)
def report_smo_expert_defects():
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
        otdel_name = ""
        if defect.doctor.otdel is not None:
            otdel_name = defect.doctor.otdel.otdel_name
        logging.warning([defect, defect.doctor])
        tr.add_data_row([[defect.patient.num, defect.patient.fam, defect.patient.im, defect.patient.ot,
                          defect.patient.birthday, defect.doctor.doctor_name, otdel_name,
                          defect.disease, defect.period_begin, defect.period_end, defect.error_list,
                          defect.error_comment, defect.sum_service, defect.sum_no_pay, defect.get_sum_total(),
                          defect.sum_penalty, defect.expert_date, defect.expert_name, defect.expert_act_number]])

    tr.close_template_file()
    return send_file(os.path.join('files', file_name), as_attachment=True, mimetype='application/vnd.ms-excel',
                     attachment_filename="дефекты.xlsx")
