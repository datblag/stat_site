from site_app import app
from flask import render_template, request, redirect, url_for, session
from site_app.forms import SearchDoctorForm
from site_app.models.reference import RefDoctors, Mkb10
from flask_login import login_required
from site_app.site_config import FLASKY_POSTS_PER_PAGE


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

