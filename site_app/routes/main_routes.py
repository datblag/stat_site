from site_app import app, db
from flask import render_template, request, redirect, url_for, flash, session
from site_app.forms import DefectEditForm, LoginForm, DefectDeleteForm, SearchDoctorForm
from site_app.models import DefectList, RefDoctors
from flask_login import current_user, login_user, login_required, logout_user
from site_app.models import User, Mkb10
from werkzeug.urls import url_parse
from site_app.site_config import FLASKY_POSTS_PER_PAGE


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
@app.route('/mkb10/<code>', methods=['GET'])
def mkb10_list(code=None):
    mkb10_parent = []
    if code:
        mkb10 = Mkb10.query.filter_by(parent_code=code).order_by(Mkb10.id)
        if mkb10:
            parent = mkb10[0].parent
            # parent = parent.parent
            while parent:
                mkb10_parent.append(parent)
                parent = parent.parent
        else:
            return redirect(url_for('index'))
    else:
        mkb10 = Mkb10.query.filter_by(parent_code=None).filter_by(code='').order_by(Mkb10.id)
    print(mkb10_parent.reverse(), mkb10_parent)
    return render_template('mkb10.html', mkb10=mkb10, mkb10_parent=mkb10_parent)


@app.route('/doctor/', methods=['GET', 'POST'])
@app.route('/doctor/<doctorid>', methods=['GET', 'POST'])
@login_required
def doctor_list(doctorid=None):
    if doctorid:
        if 'query' in session:
            session.pop('query', None)
    form = SearchDoctorForm(request.form)
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST' and form.validate_on_submit():
        session['query'] = form.data['search']
        current_filter = session['query'] if 'query' in session else None
        page = 1
        pagination = RefDoctors.query.filter(RefDoctors.doctor_name.ilike('%'+session['query']+'%')).paginate(
            page, per_page=FLASKY_POSTS_PER_PAGE,
            error_out=False)
        doctors = pagination.items
        return render_template('doctor.html', pagination=pagination, doctors=doctors, form=form, current_filter=current_filter)
    query = RefDoctors.query
    if 'query' in session:
        query = query.filter(RefDoctors.doctor_name.ilike('%'+session['query']+'%'))
    pagination = query.paginate(
        page, per_page=FLASKY_POSTS_PER_PAGE,
        error_out=False)
    # print(pagination.items, session['query'])
    doctors = pagination.items
    current_filter = session['query'] if 'query' in session else None
    return render_template('doctor.html', pagination=pagination, doctors=doctors, form=form, current_filter=current_filter)

