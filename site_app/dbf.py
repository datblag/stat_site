import logging
import dbf
import os


def generate_examinations_file(examinations, path_name, generate_file=True):
    if generate_file:
        table = dbf.Table(os.path.join(path_name, 'obsled.dbf'),
                          '''fam C(50)
                          ;im C(50)
                          ;ot C(50)
                          ;cod N(10, 0)
                          ;d_u D
                          ;dr D
                          ;doctor C(100)''',
                          codepage='cp866')
    else:
        table = dbf.Table(os.path.join(path_name, 'obsled.dbf'))

    table.open(mode=dbf.READ_WRITE)
    for exam in examinations:
        # logging.warning(exam)
        record = {}
        for key in table.field_names:
            record[key] = exam[key]
        table.append(record)

    table.close()

