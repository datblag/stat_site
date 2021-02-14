from site_app.models.mis_db import HltSmTapTable, HltLpuDoctorTable, HltTapTable, HltDocPrvdTable, HltMkabTable, OmsMkbTable
from site_app.models.mis_db import session_mis
from sqlalchemy import func, cast, and_
from sqlalchemy.types import NUMERIC
import logging
import datetime
from site_app.template_render import TemplateRender
import uuid
import os


def get_close_tap_list_by_close_doctor(prm_date_start, prm_date_end):

    query_tap = session_mis.query(HltTapTable.tapid)
    query_tap = query_tap.group_by(HltTapTable.tapid)
    query_tap = query_tap.filter(HltTapTable.dateclose >= prm_date_start)
    query_tap = query_tap.filter(HltTapTable.dateclose <= prm_date_end)
    query_tap = query_tap.filter(HltTapTable.isclosed == 1)

    query_smtap = session_mis.query(HltSmTapTable.rf_tapid, func.max(HltSmTapTable.date_p).label('max_date_p'), func.coalesce(1, 1).label('case_count')).group_by(HltSmTapTable.rf_tapid)
    query_smtap = query_smtap.having(func.count(HltSmTapTable.rf_tapid) > 1)
    query_smtap = query_smtap.filter(HltSmTapTable.rf_tapid.in_(query_tap)).subquery('subq1')

    query_smtap2 = session_mis.query(query_smtap, HltSmTapTable.rf_lpudoctorid, HltSmTapTable.rf_docprvdid).distinct().join(HltSmTapTable, and_(HltSmTapTable.rf_tapid == query_smtap.c.rf_tapid, HltSmTapTable.date_p == query_smtap.c.max_date_p))
    query_smtap2 = query_smtap2.order_by(query_smtap.c.rf_tapid).subquery('subq2')
    return query_smtap2


def rep_case_get_count_by_close_doctor(prm_date_start=None, prm_date_end=None):

    query_smtap2 = get_close_tap_list_by_close_doctor(prm_date_start=prm_date_start, prm_date_end=prm_date_end)

    query = session_mis.query((HltLpuDoctorTable.fam_v+" "+HltLpuDoctorTable.im_v+" "+HltLpuDoctorTable.ot_v).label('fio_v'),
                              HltDocPrvdTable.name, func.sum(query_smtap2.c.case_count)).join(query_smtap2, HltLpuDoctorTable.lpudoctorid == query_smtap2.c.rf_lpudoctorid)

    query = query.join(HltDocPrvdTable, query_smtap2.c.rf_docprvdid == HltDocPrvdTable.docprvdid)
    query = query.group_by(HltLpuDoctorTable.fam_v, HltLpuDoctorTable.im_v, HltLpuDoctorTable.ot_v, HltDocPrvdTable.name)
    query = query.order_by(HltLpuDoctorTable.fam_v, HltLpuDoctorTable.im_v, HltLpuDoctorTable.ot_v, HltDocPrvdTable.name)

    return query


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
    # if prm_date_start is None:
    #     date_start = '2020-03-23'
    # else:
    #     date_start = prm_date_start
    # if prm_date_end is None:
    #     date_end = '2020-03-23'
    # else:
    #     date_end = prm_date_end

    # query_smtap = session_mis.query(HltSmTapTable.rf_tapid).group_by(HltSmTapTable.rf_tapid)
    # query_smtap = query_smtap.having(func.count(HltSmTapTable.rf_tapid) > 1)

    query_smtap = get_close_tap_list_by_close_doctor(prm_date_start=prm_date_start, prm_date_end=prm_date_end)

    query = session_mis.query((HltLpuDoctorTable.fam_v+" "+HltLpuDoctorTable.im_v+" "+HltLpuDoctorTable.ot_v).label('fio_v'), HltMkabTable.num, HltMkabTable.family,
                              HltMkabTable.name, HltMkabTable.ot, HltMkabTable.date_bd, HltTapTable.dateclose, OmsMkbTable.ds)
    query = query.join(query_smtap, query_smtap.c.rf_lpudoctorid == HltLpuDoctorTable.lpudoctorid)
    query = query.join(HltTapTable, query_smtap.c.rf_tapid == HltTapTable.tapid)
    query = query.join(HltMkabTable, HltMkabTable.mkabid == HltTapTable.rf_mkabid)
    query = query.join(OmsMkbTable, OmsMkbTable.mkbid == HltTapTable.rf_mkbid)
    # query = query.filter(HltTapTable.dateclose >= date_start)
    # query = query.filter(HltTapTable.dateclose <= date_end)
    # query = query.filter(HltTapTable.tapid.in_(query_smtap))
    query = query.order_by(HltLpuDoctorTable.fam_v, HltLpuDoctorTable.im_v, HltLpuDoctorTable.ot_v, HltMkabTable.num)
    return query


def rep_case(prm_date_start=None, prm_date_end=None, prm_copy_files=None, prm_open_in_excel=None):
    if prm_date_start is None:
        date_start = '2020-03-23'
    else:
        date_start = prm_date_start
    if prm_date_end is None:
        date_end = '2020-03-23'
    else:
        date_end = prm_date_end

    if prm_copy_files is None:
        prm_copy_files = 0
    if prm_open_in_excel is None:
        prm_open_in_excel = 0

    tr = None

    recs = rep_case_get_count_by_close_doctor(prm_date_start=date_start, prm_date_end=date_end)

    recs_list = rep_case_get_list(prm_date_start=date_start, prm_date_end=date_end)

    # if prm_copy_files or prm_open_in_excel:

    # dirs_copy_name = [r'y:\Законченные случаи', r'\\terminalserver\Кили\Законченные случаи']

    file_name = str(uuid.uuid4()) + '.xlsx'
    file_full_name = os.path.join(os.getcwd(), 'site_app', 'files', file_name)

    tr = TemplateRender(3, file_name=file_full_name,
                        copyfile=False, open_in_excel=prm_open_in_excel, sheet_title='Количество')

    tr.add_header_row('За период с ' + datetime.datetime.strptime(date_start, '%Y-%m-%d').strftime('%d.%m.%Y') + \
                      ' по ' + datetime.datetime.strptime(date_end, '%Y-%m-%d').strftime('%d.%m.%Y'))
    tr.add_header_row('')

    tr.add_titles_row([['ФИО врача', 40], ['Специальность', 40], ['Закрыто случаев', 15]])
    tr.add_data_row(recs)

    tr.add_data_row([['Итого', '', '=SUM(C' + str(tr.first_data_row) + ':C' + str(tr.current_line - 1) + ')']])

    tr.add_sheet(sheet_title='Список')

    tr.add_header_row('За период с ' + datetime.datetime.strptime(date_start, '%Y-%m-%d').strftime('%d.%m.%Y') + \
                      ' по ' + datetime.datetime.strptime(date_end, '%Y-%m-%d').strftime('%d.%m.%Y'))
    tr.add_header_row('')

    tr.add_titles_row([['ФИО врача', 40], ['№ истории', 15], ['Фамилия', 30], ['Имя', 30], ['Отчество', 30],
                       ['Др', 12], ['Дата закрытия', 12], ['Диагноз', 15]])
    tr.add_data_row(recs_list, TemplateRender.align_left_top)

    tr.close_template_file()

    return file_name


if __name__ == '__main__':
    rep_case(prm_date_start='2021-01-01', prm_date_end='2021-02-14', prm_open_in_excel=True)
    # recs = rep_case_get_count_by_close_doctor(prm_date_start='2021-01-01', prm_date_end='2021-02-14')
    # total = 0
    # for rec in recs:
    #     total += rec[2]
    #     # total += 1
    #     logging.warning(rec)
    #
    # logging.warning(total)
