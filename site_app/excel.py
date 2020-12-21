import openpyxl
from openpyxl.utils import column_index_from_string
import os
import datetime
from site_app.models.mis_db import HltMkabTable, session_mis
from sqlalchemy import func
MAPPING_BY_DATE = 1
MAPPING_BY_YEAR = 0
import logging


def set_patient_num_to_excel(path_name, file_name, start_row_num, type_mapping_birthday, fam_col_index, dr_col_index,
                             result_col_index, worksheet_num=1):
    # start_row = 2
    start_row = start_row_num - 1  # нумерация с 0 !!!!!!!!!!!!!!!!!!
    # type_mapping_birthday = MAPPING_BY_DATE

    if isinstance(fam_col_index, list):
        fam_col = column_index_from_string(fam_col_index[0])
        im_col = column_index_from_string(fam_col_index[1])
        ot_col = column_index_from_string(fam_col_index[2])
    else:
        fam_col = column_index_from_string(fam_col_index)
    dr_col = column_index_from_string(dr_col_index)
    result_col_history = column_index_from_string(result_col_index)

    find_records_count = 0

    file_full_name = os.path.join(path_name, file_name)
    wb = openpyxl.load_workbook(file_full_name)
    # ws = wb.active
    ws = wb.worksheets[worksheet_num-1]

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
        if isinstance(fam_col_index, list):
            fam = row[fam_col-1].value
            im = row[im_col-1].value
            ot = row[ot_col-1].value
            if fam is None:
                continue
            if im is None:
                continue
        else:
            fam_value = row[fam_col-1].value
            if fam_value is None:
                continue
            logging.warning(fam_value)
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

        logging.warning([fam, im, ot])

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
        logging.warning(recs)
        if recs:
            find_records_count += 1
            ws.cell(row_num, result_col_history).value = recs[0].num
    logging.warning(find_records_count)
    wb.save(file_full_name)


def main():

    path_name = r'S:\20201215_узи'
    file_name = 'узи омс июнь.xlsx'
    set_patient_num_to_excel(path_name, file_name, 2, MAPPING_BY_DATE, ['A', 'B', 'C'], 'D', 'H')


if __name__ == '__main__':
    main()

