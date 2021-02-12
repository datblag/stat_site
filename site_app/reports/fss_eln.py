import uuid
from site_app.template_render import TemplateRender
import os
import psycopg2
from site_app.site_config import sql_pg_eln
import logging
import datetime


def eln_count_for_period(date_start, date_end, file_genarate=False):

    date_start_str = date_start.strftime('%d.%m.%Y')
    date_end_str = date_end.strftime('%d.%m.%Y')
    file_name = ''

    try:
        conn = psycopg2.connect(sql_pg_eln)
    except psycopg2.Error as err:
        res_str = "Connection error: {}".format(err)
        logging.warning(res_str)

    date_end_rep = date_end + datetime.timedelta(days=1)

    prm_date_start = "'" + date_start_str + "'"
    prm_date_end_rep = "'" + date_end_rep.strftime('%d.%m.%Y') + "'"

    sql = f'SELECT reason1, count(*) as cnt FROM public.fc_eln_data_history where (ln_date>={prm_date_start}) ' \
        f'and (ln_date<{prm_date_end_rep}) group by reason1 order by reason1'
    logging.warning(sql)

    res_str = 'Выписано ЭЛН'
    data = None
    try:
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()
    except psycopg2.Error as err:
        res_str = "Query error: {}".format(err)

    if file_genarate:

        file_name = str(uuid.uuid4()) + '.xlsx'
        file_full_name = os.path.join(os.getcwd(), 'site_app', 'files', file_name)
        tr = TemplateRender(3, file_name=file_full_name,
                            copyfile=False, open_in_excel=False, sheet_title='Количество ЭЛН')

        tr.add_header_row(
            'ЭЛН за период с ' + date_start_str +
            ' по ' + date_end_str)
        tr.add_header_row('')

        res_count = 0

        tr.add_titles_row([['Причина выдачи', 20], ['Количество', 8]])
        sum_cnt = 0

        if data is not None:
            for row in data:
                tr.add_data_row([[row[0], row[1]]])
                sum_cnt += row[1]
            tr.add_data_row([['Итого', sum_cnt]])
        else:
            tr.add_data_row([[res_str, res_count]])
        tr.close_template_file()

    return (data, file_name)

