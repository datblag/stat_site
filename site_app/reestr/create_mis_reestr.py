from site_app.models.mis_db import *
import logging


def main():
    tmp_department = session_mis.query(OmsDepartmentTable.departmentid, OmsDepartmentTable.rf_lpuid).\
        filter(OmsDepartmentTable.rf_kl_departmenttypeid == 3)

    # OmsDepartmentTable.department_list(OmsDepartmentTable, session_mis)

    rows = session_mis.query(HltTapTable, OmsKlDdServiceTable).join(OmsKlDdServiceTable,
                                               HltTapTable.rf_kl_DDServiceID == OmsKlDdServiceTable.kl_ddserviceid).filter(OmsKlDdServiceTable.simple == 100).limit(1000).all()
    for row in rows:
        logging.warning(row)


if __name__ == '__main__':
    main()
