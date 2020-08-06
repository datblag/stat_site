from site_app.site_config import sql_database_mis
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, VARCHAR, INT, DATE

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

engine_string_mis = f"mssql+pymssql://{sql_database_mis['sql_user']}:{sql_database_mis['sql_password']}@" \
    f"{sql_database_mis['sql_server']}/{sql_database_mis['sql_database']}"
engine_mis = create_engine(engine_string_mis, echo=True)

BaseMis = declarative_base()
metadata_mis = MetaData()
session_mis = Session(bind=engine_mis)


class HltMkab(BaseMis):
    __tablename__ = 'hlt_mkab'
    mkabid = Column(INT, primary_key=True)
    family = Column(VARCHAR(40))
    name = Column(VARCHAR(40))
    ot = Column(VARCHAR(40))
    date_bd = Column(DATE)
    num = Column(VARCHAR(40))

    def __repr__(self):
        return '<{} {} {} {}>'.format(self.family, self.name, self.ot, self.date_bd)


