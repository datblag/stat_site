from site_app.mis_db import *
import logging


def main():
    tmp_department = session_mis.query(OmsDepartmentTable.departmentid, OmsDepartmentTable.rf_lpuid).\
        filter(OmsDepartmentTable.rf_kl_departmenttypeid == 3)

    # OmsDepartmentTable.department_list(OmsDepartmentTable, session_mis)

    rows = session_mis.query(HltTapTable).limit(1000).all()
    for row in rows:
        logging.warning(row.department)


if __name__ == '__main__':
    main()
