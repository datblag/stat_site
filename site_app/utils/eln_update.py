import psycopg2
from site_app.site_config import sql_pg_eln
import logging
import time


try:
    conn = psycopg2.connect(sql_pg_eln)
except psycopg2.Error as err:
    res_str = "Connection error: {}".format(err)
    logging.warning(conn)

cur = conn.cursor()
while True:
    cur.execute('''update fc_eln_data_history set employer = '.', empl_flag=1 where employer is null''')
    conn.commit()
    logging.warning('update')
    time.sleep(10)

