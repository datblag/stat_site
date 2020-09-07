from site_app.mis_db import *
import logging


def main():
    tmp_department = session_mis.query(OmsDepartmentTable.departmentid, OmsDepartmentTable.rf_lpuid).\
        filter(OmsDepartmentTable.rf_kl_departmenttypeid == 3)
    logging.warning(session_mis.query(tmp_department))




if __name__ == '__main__':
    main()
