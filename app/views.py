# -*- coding: UTF-8 -*-
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import render_template, redirect, url_for, flash, request, abort, session
from flask_login import login_required, login_user, current_user

from app import app, login_manager
from app.forms import *
from app.models import *


@app.route('/index')
def index():
    tag = {'name': 'index'}
    if current_user.is_anonymous:
        user = None
    else:
        user = current_user
    return render_template("index.html", user=user, tag=tag)


@app.route('/add_conference', methods = ['GET', 'POST'])
@login_required
def add_conference():
    form = AddConferenceForm()
    if current_user.is_anonymous:
        user = None
    else:
        user = current_user
    tag = {'name': 'add_conference'}
    if form.validate_on_submit():
        name = form.name.data
        date = form.date.data
        place = form.place.data

        conference = Conference(name=name, date=date, place=place)
        db.session.add(conference)
        db.session.commit()
    return render_template('add_conference.html', user=user, form=form, tag=tag)


@app.route('/previewlist')
@login_required
def previewlist():
    if current_user.is_anonymous:
        user = None
    else:
        user = current_user
    tag = {'name': 'previewlist'}
    conferences = Conference.query.all()
    return render_template('previewlist.html', user=user, tag=tag, conferences=conferences)


@app.route('/preview')
@login_required
def preview():
    if current_user.is_anonymous:
        user = None
    else:
        user = current_user
    tag = {'name': 'preview'}
    conference = Conference.query.get(1)
    return render_template('preview.html', user=user, tag=tag, conference=conference)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


# 登录验证装饰器
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('User'):  # 验证session
            return func(*args, **kwargs)
        else:
            return redirect(url_for('admin.login'))
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("账号不存在")  # 操作提示信息，会在前端显示
            return redirect(url_for('login'))
        elif not user.check_pwd(password):
            flash('密码输入错误，请重新输入！')
            return redirect(url_for('login'))
        session['user'] = username  # 匹配成功，添加session
        login_user(user, form.remember_me.data)
        return redirect(request.args.get('next') or url_for('index'))  # 重定向到首页
    return render_template('login.html', form=form)


# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()p
#     return redirect(somewhere)