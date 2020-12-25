from site_app.site_config import sql_database_mis
from sqlalchemy import create_engine, MetaData, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import Column, VARCHAR, INT, DATE, BOOLEAN, func
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

engine_string_mis = f"mssql+pymssql://{sql_database_mis['sql_user']}:{sql_database_mis['sql_password']}@" \
    f"{sql_database_mis['sql_server']}/{sql_database_mis['sql_database']}"
engine_mis = create_engine(engine_string_mis, echo=True)

BaseMis = declarative_base()
metadata_mis = MetaData()
session_mis = Session(bind=engine_mis)


# карта пациента
class HltMkabTable(BaseMis):
    __tablename__ = 'hlt_mkab'
    mkabid = Column(INT, primary_key=True)
    family = Column(VARCHAR(40))
    name = Column(VARCHAR(40))
    ot = Column(VARCHAR(40))
    date_bd = Column(DATE)
    num = Column(VARCHAR(40))

    def __repr__(self):
        return '<{} {} {} {}>'.format(self.family, self.name, self.ot, self.date_bd)


# отделения
class OmsDepartmentTable(BaseMis):
    __tablename__ = 'oms_department'
    departmentid = Column(INT, primary_key=True)
    departmentname = Column(VARCHAR(255))
    rf_lpuid = Column(INT)
    rf_kl_departmenttypeid = Column(INT)
    tap_list = relationship('HltTapTable', backref='department', lazy='dynamic')

    def department_list(self, session):
        return session.query(self).filter(self.rf_kl_departmenttypeid == 3)

    def __repr__(self):
        return '<{}>'.format(self.departmentname)


# случаи заболеваний
class HltTapTable(BaseMis):
    __tablename__ = 'hlt_tap'
    tapid = Column(INT, primary_key=True)
    rf_departmentid = Column(INT, ForeignKey('oms_department.departmentid'))
    rf_kl_ddserviceid = Column(INT)
    rf_mkabid = Column(INT)
    isclosed = Column(BOOLEAN)
    rf_kl_profittypeid = Column(INT)
    dateclose = Column(DATE)
    rf_onco_signid = Column(INT)


# классификатор услуг для дополнительной диспансеризации
class OmsKlDdServiceTable(BaseMis):
    __tablename__ = 'oms_kl_ddservice'
    kl_ddserviceid = Column(INT, primary_key=True)
    code = Column(VARCHAR(50))
    name = Column(VARCHAR(255))
    date_e = Column(DATE)

    @hybrid_property
    def simple(self):
        return 100


# отчетный период
class HltReportPeriod(BaseMis):
    __tablename__ = 'hlt_reportperiod'
    reportperiodid = Column(INT, primary_key=True)
    uguid = Column(UNIQUEIDENTIFIER())


# настройки пользователей
class XUserSettings(BaseMis):
    __tablename__ = 'x_usersettings'
    usersettingid = Column(INT, primary_key=True)
    valuestr = Column(VARCHAR(500))
    property = Column(VARCHAR(50))

    def get_ogrn(self):
        # host code: SELECT ValueStr FROM x_UserSettings WHERE Property = 'ОГРН поликлиники'
        return session_mis.query(XUserSettings).filter(XUserSettings.property == 'ОГРН поликлиники').all()[0].valuestr


# справочник ЛПУ
class OmsLpu(BaseMis):
    __tablename__ = 'oms_lpu'
    lpuid = Column(INT, primary_key=True)
    c_ogrn = Column(VARCHAR(15))
    stlpu = Column(VARCHAR(1))
    rf_okatoid = Column(INT, ForeignKey('oms_okato.okatoid'))

    def get_lpuid(self, c_ogrn=''):
        # host code: SELECT ISNULL(MIN(LPUID), 0) FROM oms_LPU WHERE C_OGRN = '@C_OGRN' AND StLPU = '1';
        select = session_mis.query(func.isnull(func.min(OmsLpu.lpuid), 0).label('lpuid'))
        return select.filter(OmsLpu.c_ogrn == c_ogrn).filter(OmsLpu.stlpu == '1').all()[0].lpuid

    def get_okato(self, lpuid=''):
        # host code: SELECT TOP(1) LEFT(C_OKATO, 2) + '000' FROM oms_OKATO LEFT  JOIN oms_LPU ON  rf_OKATOID = OKATOID
        # WHERE LPUID = @LPUID  ;
        return session_mis.query(OmsLpu).get(lpuid).okato.c_okato[0:2] + '000'


class OmsOkato(BaseMis):
    __tablename__ = 'oms_okato'
    okatoid = Column(INT, primary_key=True)
    oms_lpu = relationship('OmsLpu', backref='okato', lazy='dynamic')
    oms_stf = relationship('OmsStf', backref='okato', lazy='dynamic')
    c_okato = Column(VARCHAR(15))

    # host code: SELECT ISNULL(MIN(OKATOID), 0) FROM oms_OKATO WHERE C_OKATO = '@C_OKATO';
    def get_okatoid(self, c_okato):
        return session_mis.query(OmsOkato.okatoid).filter(OmsOkato.c_okato == c_okato).all()[0].okatoid


# справочник ТФОМС
class OmsStf(BaseMis):
    __tablename__ = 'oms_stf'
    stfid = Column(INT, primary_key=True)
    rf_okato = Column(INT, ForeignKey('oms_okato.okatoid'))
