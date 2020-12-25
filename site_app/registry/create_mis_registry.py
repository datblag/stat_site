from sqlalchemy.sql.functions import min

# from site_app.models.mis_db import *
from site_app.models import mis_db
import logging
import datetime
from sqlalchemy import func
import uuid


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
        self.c_ogrn = self.mis_db.XUserSettings().get_ogrn()
        self.lpuid = self.mis_db.OmsLpu.get_lpuid(self.mis_db.OmsLpu, c_ogrn=self.c_ogrn)
        self.c_okato = self.mis_db.OmsLpu.get_okato(self.mis_db.OmsLpu, lpuid=self.lpuid)
        self.okatoid = self.mis_db.OmsOkato.get_okatoid(self.mis_db.OmsOkato, c_okato=self.c_okato)
        self.stfid = self.mis_db.session_mis.query(self.mis_db.OmsStf).filter(self.mis_db.OmsStf.rf_okato ==
                                                                    self.okatoid).all()[0].stfid

        # mis code: SELECT  '[tmpdts' +	REPLACE(LOWER(CONVERT(VARCHAR(36), NEWID())), '-', '') +	']';
        self.reestrhlt = ''.join(['[', 'tmpdts', uuid.uuid4().hex, ']'])
        self.reestrstt = ''.join(['[', 'tmpdts', uuid.uuid4().hex, ']'])

    def get_temp_tap(self):
        query = mis_db.session_mis.query(self.mis_db.OmsDepartmentTable.departmentid.label('departmentid'),
                                         self.mis_db.OmsDepartmentTable.rf_lpuid.label('lpuid'),
                                         self.mis_db.OmsKlDdServiceTable.code.label('code'),
                                         func.sign(self.mis_db.HltTapTable.rf_onco_signid).label('rf_onco_signid'))
        query = query.join(self.mis_db.HltTapTable, self.mis_db.OmsDepartmentTable.departmentid ==
                           self.mis_db.HltTapTable.rf_departmentid)
        query = query.join(self.mis_db.OmsKlDdServiceTable, self.mis_db.HltTapTable.rf_kl_ddserviceid ==
                           self.mis_db.OmsKlDdServiceTable.kl_ddserviceid)

        query = query.filter(self.mis_db.OmsDepartmentTable.rf_kl_departmenttypeid == 3)
        query = query.filter(self.mis_db.HltTapTable.rf_mkabid > 0)
        query = query.filter(self.mis_db.HltTapTable.isclosed == 1)
        query = query.filter(self.mis_db.HltTapTable.rf_kl_profittypeid == 3)
        query = query.filter(self.mis_db.HltTapTable.dateclose.between(self.date_begin, self.date_end))
        query = query.filter(self.mis_db.OmsKlDdServiceTable.date_e > self.mis_db.HltTapTable.dateclose)




        return query

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
    logging.warning(current_registry.get_temp_tap())
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
