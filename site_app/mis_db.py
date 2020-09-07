from site_app.site_config import sql_database_mis
from sqlalchemy import create_engine, MetaData, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, VARCHAR, INT, DATE

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
    rf_DepartmentID = Column(INT, ForeignKey('oms_department.departmentid'))


# классификатор услуг для дополнительной диспансеризации
class OmsKlDdServiceTable(BaseMis):
    __tablename__ = 'oms_kl_ddservice'
    kl_ddserviceid = Column(INT, primary_key=True)
    code = Column(VARCHAR(50))
    name = Column(VARCHAR(255))
