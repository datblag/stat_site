from site_app import app
from flask import render_template, request, redirect, url_for, flash
from site_app.forms import LoginForm, PolisForm
from flask_login import current_user, login_user, login_required, logout_user
from site_app.models import User
from werkzeug.urls import url_parse


@app.template_filter('formatdate')
def format_date(value):
    if value is None:
        return ""
    return value.strftime('%d.%m.%Y')


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


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PolisForm()
    if form.validate_on_submit():
        pass
    return render_template('index.html', form=form)


@app.errorhandler(403)
def page_not_found(e):
    return 'Нет доступа'


@app.errorhandler(404)
def page_not_found(e):
    return 'Страница не найдена'

