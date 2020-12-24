from sqlalchemy.sql.functions import min

# from site_app.models.mis_db import *
from site_app.models import mis_db
import logging
import datetime
from sqlalchemy import func


class MisRegistry:
    date_old = None
    date_begin = None
    date_end = None
    mis_db = None
    c_ogrn = None
    lpuid = None
    c_okato = None
    okatoid = None
    stfid = None
    reestrhlt = None
    reestrstt = None

    def __init__(self, date_old, date_begin, date_end, mis_db):
        self.date_old = date_old
        self.date_begin = date_begin
        self.date_end = date_end
        self.mis_db = mis_db
        self.c_ogrn = mis_db.XUserSettings().get_ogrn()
        self.lpuid = mis_db.OmsLpu.get_lpuid(mis_db.OmsLpu, c_ogrn=self.c_ogrn)
        self.c_okato = mis_db.OmsLpu.get_okato(mis_db.OmsLpu, lpuid=self.lpuid)
        self.okatoid = mis_db.OmsOkato.get_okatoid(mis_db.OmsOkato, c_okato=self.c_okato)
        self.stfid = mis_db.session_mis.query(mis_db.OmsStf).filter(mis_db.OmsStf.rf_okato == self.okatoid).all()[0].stfid
        self.reestrhlt = mis_db.session_mis.query('''
        (SELECT '[tmpdts'+	REPLACE(LOWER(CONVERT(VARCHAR(36), NEWID())), '-', '')+	']')''').all()[0]
        self.reestrstt = mis_db.session_mis.query('''
        (SELECT '[tmpdts'+	REPLACE(LOWER(CONVERT(VARCHAR(36), NEWID())), '-', '')+	']')''').all()[0]

    def process_registry_by_type(self, reg_type):
        pass


def main():
    # установка параметров
    date_old = datetime.date(2020, 7, 23) # поздноподанные с даты
    date = datetime.date(2020, 7, 23)
    date_begin = datetime.date(2020, 8, 23)
    date_end = datetime.date(2020, 9, 22)

    current_registry = MisRegistry(date_old=date_old, date_begin=date_begin, date_end=date_end, mis_db=mis_db)
    logging.warning(current_registry.date_old)

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

    # c_ogrn = XUserSettings().get_ogrn()
    logging.warning(['ОГРН', current_registry.c_ogrn])
    logging.warning(['lpuid', current_registry.lpuid])

    # lpuid = OmsLpu.get_lpuid(OmsLpu, c_ogrn=c_ogrn)
    #
    #
    # c_okato = session_mis.query(OmsLpu).get(lpuid).okato.c_okato[0:2]+'000'
    logging.warning(['c_okato', current_registry.c_okato])
    #
    # okatoid = OmsOkato.get_okatoid(OmsOkato, c_okato=c_okato)
    logging.warning(['okatoid', current_registry.okatoid])
    #
    # r = session_mis.query(OmsStf).filter(OmsStf.rf_okato == okatoid).all()
    logging.warning(['stfid', current_registry.stfid])
    logging.warning(['reestrhlt', current_registry.reestrhlt])
    logging.warning(['reestrstt', current_registry.reestrstt])
    #
    # # tmp_department = session_mis.query(OmsDepartmentTable.departmentid, OmsDepartmentTable.rf_lpuid).\
    # #     filter(OmsDepartmentTable.rf_kl_departmenttypeid == 3)
    #
    # # OmsDepartmentTable.department_list(OmsDepartmentTable, session_mis)
    #
    # # rows = session_mis.query(HltTapTable, OmsKlDdServiceTable).join(OmsKlDdServiceTable,
    # #                                            HltTapTable.rf_kl_DDServiceID == OmsKlDdServiceTable.kl_ddserviceid).filter(OmsKlDdServiceTable.simple == 100).limit(10).all()
    # # for row in rows:
    # #     logging.warning(row)


if __name__ == '__main__':
    main()
