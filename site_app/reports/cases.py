from site_app.models.mis_db import HltSmTapTable, HltLpuDoctorTable, HltTapTable, HltDocPrvdTable, HltMkabTable, OmsMkbTable
from site_app.models.mis_db import session_mis
from sqlalchemy import func, cast
from sqlalchemy.types import NUMERIC
import datetime
from site_app.template_render import TemplateRender


def rep_case_get_count(prm_date_start=None, prm_date_end=None):
    if prm_date_start is None:
        date_start = '2020-03-23'
    else:
        date_start = prm_date_start
    if prm_date_end is None:
        date_end = '2020-03-23'
    else:
        date_end = prm_date_end

    query_smtap = session_mis.query(HltSmTapTable.rf_tapid).group_by(HltSmTapTable.rf_tapid)
    query_smtap = query_smtap.having(func.count(HltSmTapTable.rf_tapid) > 1)

    query = session_mis.query((HltLpuDoctorTable.fam_v+" "+HltLpuDoctorTable.im_v+" "+HltLpuDoctorTable.ot_v).label('fio_v'),
                              HltDocPrvdTable.name, func.sum(cast(HltTapTable.isclosed, NUMERIC(10, 0))).label('case'))
    query = query.join(HltTapTable, HltTapTable.rf_lpudoctorid == HltLpuDoctorTable.lpudoctorid)
    query = query.join(HltDocPrvdTable, HltTapTable.rf_docprvdid == HltDocPrvdTable.docprvdid)
    query = query.filter(HltTapTable.dateclose >= date_start)
    query = query.filter(HltTapTable.dateclose <= date_end)
    query = query.filter(HltTapTable.tapid.in_(query_smtap))
    query = query.group_by(HltLpuDoctorTable.fam_v, HltLpuDoctorTable.im_v, HltLpuDoctorTable.ot_v, HltDocPrvdTable.name)
    query = query.order_by(HltLpuDoctorTable.fam_v, HltLpuDoctorTable.im_v, HltLpuDoctorTable.ot_v, HltDocPrvdTable.name)

    return query.all()


def rep_case_get_list(prm_date_start=None, prm_date_end=None):
    if prm_date_start is None:
        date_start = '2020-03-23'
    else:
        date_start = prm_date_start
    if prm_date_end is None:
        date_end = '2020-03-23'
    else:
        date_end = prm_date_end

    query_smtap = session_mis.query(HltSmTapTable.rf_tapid).group_by(HltSmTapTable.rf_tapid)
    query_smtap = query_smtap.having(func.count(HltSmTapTable.rf_tapid) > 1)

    query = session_mis.query((HltLpuDoctorTable.fam_v+" "+HltLpuDoctorTable.im_v+" "+HltLpuDoctorTable.ot_v).label('fio_v'), HltMkabTable.num, HltMkabTable.family,
                              HltMkabTable.name, HltMkabTable.ot, HltMkabTable.date_bd, HltTapTable.dateclose, OmsMkbTable.ds)
    query = query.join(HltTapTable, HltTapTable.rf_lpudoctorid == HltLpuDoctorTable.lpudoctorid)
    query = query.join(HltMkabTable, HltMkabTable.mkabid == HltTapTable.rf_mkabid)
    query = query.join(OmsMkbTable, OmsMkbTable.mkbid == HltTapTable.rf_mkbid)
    query = query.filter(HltTapTable.dateclose >= date_start)
    query = query.filter(HltTapTable.dateclose <= date_end)
    query = query.filter(HltTapTable.tapid.in_(query_smtap))
    query = query.order_by(HltLpuDoctorTable.fam_v, HltLpuDoctorTable.im_v, HltLpuDoctorTable.ot_v, HltMkabTable.num)
    return query.all()


def rep_case(prm_date_start=None, prm_date_end=None, prm_copy_files=None, prm_open_in_excel=None):
    if prm_copy_files is None:
        prm_copy_files = 0
    if prm_open_in_excel is None:
        prm_open_in_excel = 0

    tr = None

    if prm_copy_files or prm_open_in_excel:

        dirs_copy_name = [r'y:\Законченные случаи', r'\\terminalserver\Кили\Законченные случаи']
        tr = TemplateRender(3, file_name=r'законченные случаи по врачам c ' + prm_date_start + ' по ' + prm_date_end + '.xlsx',
                            copyfile=prm_copy_files, open_in_excel=True,
                            dirs_copy_name=dirs_copy_name, sheet_title='Количество')

        tr.add_header_row('За период с ' + datetime.datetime.strptime(prm_date_start, '%Y-%m-%d').strftime('%d.%m.%Y') + \
                          ' по ' + datetime.datetime.strptime(prm_date_end, '%Y-%m-%d').strftime('%d.%m.%Y'))
        tr.add_header_row('')

    recs = rep_case_get_count(prm_date_start=prm_date_start, prm_date_end=prm_date_end)

    if prm_open_in_excel or prm_copy_files:

        tr.add_titles_row([['ФИО врача', 40], ['Специальность', 40], ['Закрыто случаев', 15]])
        tr.add_data_row(recs)

        tr.add_data_row([['Итого', '', '=SUM(C' + str(tr.first_data_row) + ':C' + str(tr.current_line - 1) + ')']])

    # tr.close_template_file()
    recs = rep_case_get_list()

    if prm_open_in_excel or prm_copy_files:
        tr.add_sheet(sheet_title='Список')

        tr.add_header_row('За период с ' + datetime.datetime.strptime(prm_date_start, '%Y-%m-%d').strftime('%d.%m.%Y') + \
                          ' по ' + datetime.datetime.strptime(prm_date_end, '%Y-%m-%d').strftime('%d.%m.%Y'))
        tr.add_header_row('')

        tr.add_titles_row([['ФИО врача', 40], ['№ истории', 15], ['Фамилия', 30], ['Имя', 30], ['Отчество', 30],
                           ['Др', 12], ['Дата закрытия', 12], ['Диагноз', 15]])
        tr.add_data_row(recs, TemplateRender.align_left_top)
        tr.close_template_file()


if __name__ == '__main__':
    rep_case()

