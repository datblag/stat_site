from site_app import app, db
from flask import render_template, Response, request, redirect, url_for, flash
from site_app.forms import DefectEditForm, LoginForm, DefectDeleteForm
import json
from site_app.models import DefectList, RefDoctors, RefDefectTypes
from flask_login import current_user, login_user, login_required, logout_user
from site_app.models import User, Mkb10
from werkzeug.urls import url_parse
from site_app.site_config import FLASKY_POSTS_PER_PAGE

doctors = []
doctor_dbf = db.session.query(RefDoctors).all()
for rec in doctor_dbf:
    doctors.append({'label': rec.doctor_stat_code + " " + rec.doctor_name.strip(), 'value': rec.doctor_stat_code})


defects = []
defect_recs = db.session.query(RefDefectTypes).all()
for rec in defect_recs:
    defects.append({'label': rec.defect_type_code + " " + rec.defect_name.strip(), 'value': rec.defect_type_code})


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_login=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@app.route('/defect/', methods=['GET'])
@login_required
def defect_list():
    page = request.args.get('page', 1, type=int)
    pagination = DefectList.query.filter(DefectList.is_deleted != 1).paginate(
        page, per_page=FLASKY_POSTS_PER_PAGE,
        error_out=False)

    # defects = db.session.query(DefectList).filter(DefectList.is_deleted != 1).all()
    defects = pagination.items
    return render_template('defect.html', pagination=pagination, defects=defects)


@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    print(doctors)
    return Response(json.dumps(doctors), mimetype='application/json')


@app.route('/_autocomplete2', methods=['GET'])
def autocomplete2():
    print(defects)
    return Response(json.dumps(defects), mimetype='application/json')


@app.route('/defect/<int:defectid>', methods=['GET', 'POST'])
@login_required
def defect_edit(defectid=0):
    form = DefectEditForm(request.form)
    if defectid == 0:
        pass
    else:
        defect_rec = DefectList.query.get_or_404(defectid)
    # print(form.validate_on_submit(), request.method, request)
    if request.method == 'POST' and form.validate_on_submit():
        if defectid == 0:
            defect_rec = DefectList()
            defect_rec.is_deleted = 0
        defect_rec.history = form.history.data

        doctor_ref_rec = RefDoctors.query.filter_by(doctor_stat_code=form.doctor_code.data.strip()).first()
        defect_rec.doctor_id_ref = doctor_ref_rec.doctor_id

        defect_rec.error_list = form.defect_codes.data
        defect_rec.error_comment = form.defect_comment.data

        defect_rec.disease = form.disease.data

        defect_rec.period_begin = form.period_start.data
        defect_rec.period_end = form.period_end.data

        defect_rec.sum_service = form.sum_service.data
        defect_rec.sum_no_pay = form.sum_no_pay.data
        defect_rec.sum_penalty = form.sum_penalty.data

        db.session.add(defect_rec)
        db.session.commit()
        return redirect(url_for('defect_list'))

    if defectid != 0:
        form.history.data = defect_rec.history

        if defect_rec.doctor_id_ref:
            doctor_ref_rec = RefDoctors.query.get(defect_rec.doctor_id_ref)
            if doctor_ref_rec:
                form.doctor_code.data = doctor_ref_rec.doctor_stat_code
            else:
                form.doctor_code.data = ""

        form.defect_codes.data = defect_rec.error_list
        form.defect_comment.data = defect_rec.error_comment

        form.disease.data = defect_rec.disease

        form.period_start.data = defect_rec.period_begin
        form.period_end.data = defect_rec.period_end

        print(defect_rec.sum_service)

        form.sum_service.data = defect_rec.sum_service
        form.sum_no_pay.data = defect_rec.sum_no_pay
        form.sum_penalty.data = defect_rec.sum_penalty

    return render_template('defectedit.html', defectid=str(defectid), form=form)


@app.route('/defect_delete/<int:defectid>', methods=['GET', 'POST'])
@login_required
def defect_delete(defectid=0):
    form = DefectDeleteForm(request.form)
    if defectid == 0 or defectid is None:
        return redirect(url_for('defect_list'))
    if request.method == 'POST' and form.validate_on_submit():
        d = DefectList.query.filter_by(defect_id=defectid).first()
        d.is_deleted = 1
        db.session.add(d)
        db.session.commit()
        return redirect(url_for('defect_list'))
    return render_template('defectdelete.html', defectid=str(defectid), form=form)


@app.route('/mkb10/', methods=['GET'])
def mkb10_list():
    mkb10 = Mkb10.query.filter_by(parent_code='').filter_by(code='').order_by(Mkb10.id)
    return render_template('mkb10.html', mkb10=mkb10)


@app.route('/doctor/', methods=['GET'])
@login_required
def doctor_list():
    page = request.args.get('page', 1, type=int)
    pagination = RefDoctors.query.paginate(
        page, per_page=FLASKY_POSTS_PER_PAGE,
        error_out=False)

    doctors = pagination.items
    return render_template('doctor.html', pagination=pagination, doctors=doctors)

