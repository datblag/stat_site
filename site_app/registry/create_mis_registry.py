from sqlalchemy.sql.functions import min

# from site_app.models.mis_db import *
from site_app.models import mis_db
import logging
import datetime
from sqlalchemy import func, and_
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
    registry_type = None
    temp_tap = None

    def __init__(self, date_old, date_begin, date_end, mis_db, registry_type):
        # registry_type: 0 основной (заболевания), 1 дд, 3 онко
        self.date_old = date_old
        self.date_begin = date_begin
        self.date_end = date_end
        self.mis_db = mis_db
        self.c_ogrn = self.mis_db.XUserSettingsTable().get_ogrn()
        self.lpuid = self.mis_db.OmsLpuTable.get_lpuid(self.mis_db.OmsLpuTable, c_ogrn=self.c_ogrn)
        self.c_okato = self.mis_db.OmsLpuTable.get_okato(self.mis_db.OmsLpuTable, lpuid=self.lpuid)
        self.okatoid = self.mis_db.OmsOkatoTable.get_okatoid(self.mis_db.OmsOkatoTable, c_okato=self.c_okato)
        self.stfid = self.mis_db.session_mis.query(self.mis_db.OmsStfTable).filter(self.mis_db.OmsStfTable.rf_okato ==
                                                                                   self.okatoid).all()[0].stfid

        # mis code: SELECT  '[tmpdts' +	REPLACE(LOWER(CONVERT(VARCHAR(36), NEWID())), '-', '') +	']';
        self.reestrhlt = ''.join(['[', 'tmpdts', uuid.uuid4().hex, ']'])
        self.reestrstt = ''.join(['[', 'tmpdts', uuid.uuid4().hex, ']'])
        self.registry_type = registry_type
        if registry_type == 0:
            self.temp_tap = self.get_temp_tap_h()
        elif registry_type == 1:
            self.temp_tap = self.get_temp_tap_dd()
        elif registry_type == 3:
            self.temp_tap = self.get_temp_tap_onko()

    def get_temp_tap(self):

        query = self.mis_db.OmsDepartmentTable.get_tmp_department(self.mis_db.OmsDepartmentTable,
                                                                  mis_db.session_mis)

        query = query.add_columns(self.mis_db.OmsKlDdServiceTable.code.label('code'),
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

    def get_temp_tap_h(self):
        query = self.get_temp_tap()
        query = query.filter(self.mis_db.HltTapTable.rf_kl_ddserviceid == 0)
        query = query.filter(func.sign(self.mis_db.HltTapTable.rf_onco_signid) == 0)
        return query

    def get_temp_tap_dd(self):
        query = self.get_temp_tap()
        query = query.filter(self.mis_db.HltTapTable.rf_kl_ddserviceid > 0)
        return query

    def get_temp_tap_onko(self):
        query = self.get_temp_tap()
        query = query.filter(self.mis_db.HltTapTable.rf_kl_ddserviceid == 0)
        query = query.filter(func.sign(self.mis_db.HltTapTable.rf_onco_signid) == 1)
        return query

    def get_reestrhlt(self):
        # выбираем услуги для реестра
        # cte() subquery()
        query = self.temp_tap
        query = query.join(self.mis_db.HltSmTapTable, self.mis_db.HltTapTable.tapid ==
                           self.mis_db.HltSmTapTable.rf_tapid, isouter=True)
        query = query.join(self.mis_db.HltReestrMhSmTapTable, and_(self.mis_db.HltReestrMhSmTapTable.rf_smtapid ==
                                                                   self.mis_db.HltSmTapTable.smtapid,
                                                                   self.mis_db.HltReestrMhSmTapTable.rf_reestrmhid > 0),
                           isouter=True)
        query = query.join(self.mis_db.OmsServiceMedicalTable, self.mis_db.OmsServiceMedicalTable.servicemedicalid ==
                           self.mis_db.HltSmTapTable.rf_omsservicemedicalid,
                           isouter=True)

        query = query.filter(self.mis_db.HltSmTapTable.count > 0)
        query = query.filter(self.mis_db.HltSmTapTable.flagbill == 1)
        query = query.filter(self.mis_db.HltReestrMhSmTapTable.rf_smtapid == None)
        query = query.add_columns(self.mis_db.HltSmTapTable.smtapid.label('smtapid'),
                                  self.mis_db.HltSmTapTable.rf_tapid.label('rf_tapid'),
                                  self.mis_db.HltSmTapTable.count.label('count'),
                                  self.mis_db.HltSmTapTable.date_p.label('date_p'),
                                  self.mis_db.HltSmTapTable.flagcomplete.label('flagcomplete'),
                                  self.mis_db.HltSmTapTable.flagpay.label('flagpay'),
                                  self.mis_db.OmsServiceMedicalTable.iscomplex.label('iscomplex'))
        return query


def main():
    # установка параметров
    date_old = datetime.date(2020, 7, 23) # поздноподанные с даты
    date = datetime.date(2020, 7, 23)
    date_begin = datetime.date(2020, 11, 23)
    date_end = datetime.date(2020, 12, 23)

    # registry_type: 0 - основной, 1 - ДД, 2 - ВМП, 3 - ОНКО
    current_registry = MisRegistry(date_old=date_old, date_begin=date_begin, date_end=date_end, mis_db=mis_db,
                                   registry_type=0)
    logging.warning(current_registry.date_old)

    dd = 0
    # if reg_type == 1:
    #     dd = 1
    #
    # hmp = 0
    # if reg_type == 2:
    #     hmp = 1
    #
    # onco = 0
    # if reg_type == 3:
    #     onco = 1

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
    # logging.warning(current_registry.temp_tap)
    logging.warning(current_registry.get_reestrhlt())

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
