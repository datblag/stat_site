import csv
import io
from site_app.models import Mkb10
from site_app import db
import datetime


with io.open(r'site_app\files\mkb10.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=',')
    for line in reader:
        ds = Mkb10()
        ds.id = line['id']
        ds.rec_code = line['rec_code']
        ds.parent_code = line['parent_code']
        ds.code = line['code']
        ds.name = line['name']
        ds.actual = True if line['actual'] else False
        if line['date']:
            ds.date = datetime.datetime.strptime(line['date'], '%d.%m.%Y')
        ds.addl_code = ds.addl_code
        db.session.add(ds)

db.session.commit()

