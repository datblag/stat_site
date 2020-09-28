import dbf
from site_app.site_config import STAT_PATH
import os
from site_app import db
from site_app.models.reference import RefDoctors, RefDefectTypes, RefOtdels, RefBureauMse, RefDisabilityGroup
import logging


def load_disability_group():
    dg = RefDisabilityGroup()
    dg.disability_group_name = '1 группа'
    db.session.add(dg)

    dg = RefDisabilityGroup()
    dg.disability_group_name = '2 группа'
    db.session.add(dg)

    dg = RefDisabilityGroup()
    dg.disability_group_name = '3 группа'
    db.session.add(dg)

    db.session.commit()


def load_bureau_mse():
    b = RefBureauMse()
    b.bureau_name = 'Бюро №1'
    db.session.add(b)

    b = RefBureauMse()
    b.bureau_name = 'Бюро №2'
    db.session.add(b)

    b = RefBureauMse()
    b.bureau_name = 'Бюро №3'
    db.session.add(b)

    b = RefBureauMse()
    b.bureau_name = 'Бюро №4'
    db.session.add(b)

    b = RefBureauMse()
    b.bureau_name = 'Бюро №7'
    db.session.add(b)

    b = RefBureauMse()
    b.bureau_name = 'Бюро №14'
    db.session.add(b)

    db.session.commit()


def load_doctors():
    logging.warning("doctors load start")
    doctor_dbf = dbf.Table(os.path.join(STAT_PATH, 'doctor.dbf'))
    doctor_dbf.open()
    for rec in doctor_dbf:
        doctor_recs = db.session.query(RefDoctors).filter_by(doctor_stat_code=rec["SCODE"]).all()
        if not doctor_recs:
            doctor_rec = RefDoctors(doctor_stat_code=rec["SCODE"], doctor_name=rec["NAME"].strip())
            db.session.add(doctor_rec)
            db.session.commit()
        else:
            doctor_rec_cur = doctor_recs[0]
            otdel_rec = db.session.query(RefOtdels).filter_by(otdel_stat_code=rec["SECTION"].strip()).first()
            doctor_rec_cur.otdel = otdel_rec
            db.session.add(doctor_rec_cur)
            db.session.commit()
        logging.warning(doctor_recs)

    logging.warning("doctors load complete")
    doctor_dbf.close()


def load_otdels():
    logging.warning("otdels load start")
    strings_dbf = dbf.Table(os.path.join(STAT_PATH, 'strings.dbf'))
    strings_dbf.open()
    for rec in strings_dbf:
        if rec["CODE"] == 5:
            logging.warning(rec["SCODE"])

            otdel_recs = db.session.query(RefOtdels).filter_by(otdel_stat_code=rec["SCODE"].strip()).all()
            if not otdel_recs:
                otdel_rec = RefOtdels(otdel_stat_code=rec["SCODE"].strip(), otdel_name=rec["NAME"].strip())
                db.session.add(otdel_rec)
                db.session.commit()

    logging.warning("otdels load complete")
    strings_dbf.close()


def load_defects():

    defect_types_dbf = dbf.Table(r'site_app\files\defect_type.dbf')
    defect_types_dbf.open()

    for rec in defect_types_dbf:
        defect_type_recs = db.session.query(RefDefectTypes).filter_by(defect_type_code=rec["SCODE"].strip()).all()
        if not defect_type_recs:
            defect_type = RefDefectTypes(defect_type_code=rec["SCODE"].strip(), defect_name=rec["NAME"].strip())
            db.session.add(defect_type)
            db.session.commit()
        logging.warning(defect_type_recs)

    logging.warning("ALL")
    defect_types_dbf.close()


