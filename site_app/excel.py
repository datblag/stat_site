import openpyxl
from openpyxl.utils import column_index_from_string
import os
import datetime
from site_app.models.mis_db import HltMkabTable, session_mis
from sqlalchemy import func
MAPPING_BY_DATE = 1
MAPPING_BY_YEAR = 0
import logging


def main():
    path_name = r's:\20201201_госпитализация'
    file_name = os.path.join(path_name, '11_2020.xlsx')
    start_row = 2
    start_row = start_row - 1  # нумерация с 0 !!!!!!!!!!!!!!!!!!
    type_mapping_birthday = MAPPING_BY_DATE

    fam_col = column_index_from_string('B')
    dr_col = column_index_from_string('C')
    result_col_history = column_index_from_string('H')

    find_records_count = 0

    wb = openpyxl.load_workbook(file_name)
    ws = wb.active

    if ws.max_column <= result_col_history:
        ws.cell(1, result_col_history).value = ''

    for row_num, row in enumerate(ws.iter_rows()):
        if row_num < start_row:
            continue
        row_num += 1
        year_bird = row[dr_col-1].value
        fam = None
        im = None
        ot = None
        fam_value = row[fam_col-1].value
        if fam_value is None:
            continue
        print(fam_value)
        fio_list = fam_value.strip().split(' ', 1)
        if len(fio_list) > 1:
            fam = fio_list[0]
            fam_value = fio_list[1]
            fio_list = fam_value.strip().split(' ', 1)
            im = fio_list[0]
            if len(fio_list) > 1:
                ot = fio_list[1]
        else:
            continue

        print(fam, im, ot)

        query = session_mis.query(HltMkabTable.num)
        query = query.filter(func.rtrim(func.ltrim(HltMkabTable.family)) == fam.strip())
        query = query.filter(func.rtrim(func.ltrim(HltMkabTable.name)) == im.strip())
        if ot is not None:
            query = query.filter(func.rtrim(func.ltrim(HltMkabTable.ot)) == ot.strip())

        if type_mapping_birthday == MAPPING_BY_YEAR:
            query = query.filter(HltMkabTable.date_bd >= datetime.date(year=year_bird, month=1, day=1))
            query = query.filter(HltMkabTable.date_bd <= datetime.date(year=year_bird, month=12, day=31))
        elif type_mapping_birthday == MAPPING_BY_DATE:
            query = query.filter(HltMkabTable.date_bd == year_bird)
        recs = query.all()
        print(recs)
        if recs:
            find_records_count += 1
            ws.cell(row_num, result_col_history).value = recs[0].num
    print(find_records_count)
    wb.save(file_name)


if __name__ == '__main__':
    main()

