from site_app.models.mis_db import *
import logging
import datetime
from sqlalchemy import func


def main():
    # установка параметров
    date = datetime.date(2020, 7, 23)  # поздноподанные с даты
    datebegin = datetime.date(2020, 8, 23)
    dateend = datetime.date(2020, 9, 22)
    reg_type = 0  # 0 - основной, 1 - ДД, 2 - ВМП, 3 - ОНКО
    dd = 0
    if reg_type == 1:
        dd = 1

    hmp = 0
    if reg_type == 2:
        hmp = 1

    onco = 0
    if reg_type == 3:
        onco = 1

    c_ogrn = XUserSettings().get_ogrn()
    logging.warning(['ОГРН', c_ogrn])

    lpuid = OmsLpu.get_lpuid(OmsLpu, c_ogrn=c_ogrn)

    logging.warning(lpuid)

    c_okato = session_mis.query(OmsLpu).get(lpuid).okato.c_okato[0:2]+'000'
    logging.warning(c_okato)

    okatoid = OmsOkato.get_okatoid(OmsOkato, c_okato=c_okato)
    logging.warning(okatoid)

    r = session_mis.query(OmsStf).filter(OmsStf.rf_okato == okatoid).all()
    logging.warning(r[0].stfid)

    # tmp_department = session_mis.query(OmsDepartmentTable.departmentid, OmsDepartmentTable.rf_lpuid).\
    #     filter(OmsDepartmentTable.rf_kl_departmenttypeid == 3)

    # OmsDepartmentTable.department_list(OmsDepartmentTable, session_mis)

    # rows = session_mis.query(HltTapTable, OmsKlDdServiceTable).join(OmsKlDdServiceTable,
    #                                            HltTapTable.rf_kl_DDServiceID == OmsKlDdServiceTable.kl_ddserviceid).filter(OmsKlDdServiceTable.simple == 100).limit(10).all()
    # for row in rows:
    #     logging.warning(row)


if __name__ == '__main__':
    main()
