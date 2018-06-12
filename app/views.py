# -*- coding: UTF-8 -*-
import datetime
from urllib.parse import urlparse, urljoin

import os
from flask import render_template, redirect, url_for, flash, request, abort, jsonify, g, send_from_directory
from flask_login import login_required, login_user, current_user, logout_user
from flask_bootstrap import Bootstrap

from app import app, login_manager, ALLOWED_EXTENSIONS
from app.forms import *
from app.models import *
from werkzeug.utils import secure_filename
import os

Bootstrap(app)


@app.route('/')
@app.route('/index')
def index():
    tag = {'name': 'index'}
    if current_user.is_anonymous:
        user = None
    else:
        user = current_user
    return render_template("index.html", user=user, tag=tag)


def is_image(filename):
    ALLOWED = set(['png', 'jpg', 'jpeg'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED


@app.route('/add_conference/<conference_id>', methods=['GET', 'POST'])
@login_required
def add_conference(conference_id):
    form = AddConferenceForm()
    file_url = None
    if current_user.is_anonymous:
        user = None
    else:
        user = current_user
    tag = {'name': 'add_conference'}
    if conference_id != '0':
        conference = Conference.query.get(conference_id)
        form.name.data = conference.name
        form.date.data = '%04d-%02d-%02dT%02d:%02d'%(conference.date.year,conference.date.month,conference.date.day,conference.date.hour,conference.date.minute)
        form.duration.data = '%02d:%02d'%(conference.duration.seconds/3600,conference.duration.seconds/60-60*(conference.duration.seconds/3600))
        form.place.data = conference.place
        form.host.data = conference.host
        form.introduction.data = conference.introduction
        form.guest_intro.data = conference.guest_intro
        form.remark.data = conference.remark

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash(message='本次提交未上传海报', category='info')
            return render_template('add_conference.html', user=user, form=form, tag=tag, is_success=False)
        f = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if f.filename == '':
            flash(message='No selected file', category='danger')
            return render_template('add_conference.html', user=user, form=form, tag=tag, is_success=False)
        elif not is_image(f.filename):
            flash(message='图片必须是png/jpg/jpeg格式', category='danger')
            return render_template('add_conference.html', user=user, form=form, tag=tag, is_success=False)
        elif f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/'))
            file_url = 'https://dszdsz.cn/static' + url_for('uploaded_file', filename=filename)
        else:
            flash('图片上传失败', category='danger')
            return render_template('add_conference.html', user=user, form=form, tag=tag, is_success=False)

    if form.validate_on_submit():
        form = AddConferenceForm()
        admin_id = user.id
        name = form.name.data
        date = form.date.data
        date = datetime.datetime.strptime(date,'%Y-%m-%dT%H:%M')
        place = form.place.data

        duration = form.duration.data
        duration = datetime.datetime.strptime(duration, '%H:%M')
        hour = duration.hour
        minute = duration.minute
        duration = datetime.timedelta(hours=hour, minutes=minute, seconds=0)

        introduction = form.introduction.data
        host = form.host.data
        guest_intro = form.guest_intro.data
        remark = form.remark.data
        status = "未发布"
        create_time = datetime.datetime.today()

        if conference_id == '0':
            conference = Conference(admin_id=admin_id, name=name, date=date, place=place, duration=duration,
                                introduction=introduction, host=host, guest_intro=guest_intro, remark=remark,
                                status=status, create_time=create_time, image=file_url)
            print(conference.to_dict())
            db.session.add(conference)
            db.session.commit()
        else:
            conference = Conference.query.get(conference_id)
            conference.admin_id = admin_id
            conference.name = name
            conference.date = date
            conference.place = place
            conference.duration = duration
            conference.introduction = introduction
            conference.host = host
            conference.guest_intro = guest_intro
            conference.remark = remark
            conference.create_time = create_time
            conference.status = status
            conference.image = file_url
            db.session.commit()
        flash(message='会议提交成功，请在审阅后发布', category='success')
        # return render_template('add_conference.html', user=user, tag=tag, is_success=True)
        return redirect(url_for('previewlist'))
    return render_template('add_conference.html', user=user, form=form, tag=tag, is_success=False)


@app.route('/previewlist')
@login_required
def previewlist():
    if current_user.is_anonymous:
        user = None
    else:
        user = current_user
    tag = {'name': 'previewlist'}
    for conference in Conference.query.all():
        if conference.status == '已发布':
            now = datetime.datetime.now()
            if now > conference.date + conference.duration:
                conference.status = '已结束'
                db.session.commit()
    conferences = Conference.query.order_by(db.desc(Conference.id)).all()
    return render_template('previewlist.html', user=user, tag=tag, conferences=conferences)


@app.route('/preview/<conference_id>')
@login_required
def preview(conference_id):
    if current_user.is_anonymous:
        user = None
    else:
        user = current_user
    tag = {'name': 'preview'}
    conference = Conference.query.get(conference_id)
    if conference is None:
        flash(message='Error', category='danger')
        return redirect(url_for(preview))
    else:
        return render_template('preview.html', user=user, tag=tag, conference=conference)


@app.route('/examine/<conference_id>')
@login_required
def examine(conference_id):
    user = current_user
    tag = {'name': 'examine'}
    conference = Conference.query.get(conference_id)
    if conference is None:
        flash(message='Error', category='danger')
        return redirect(url_for('previewlist'))
    enrolls = Enroll.query.filter_by(conference_id=conference_id).all()
    users_dict = []
    for e in enrolls:
        u = User.query.get(e.user_id)
        u_dict = u.to_dict()
        u_dict['status'] = e.status
        users_dict.append(u_dict)
    return render_template('examine.html', user=user, tag=tag, conference=conference, users=users_dict)


@app.route('/accept_enroll/<conference_id>/<user_id>')
def accept_enroll(conference_id, user_id):
    print('accept_enroll conf:' + conference_id + ' user:' + user_id)
    e = Enroll.query.filter_by(user_id=user_id, conference_id=conference_id).first()
    if e is None:
        flash(message='Error', category='danger')
    else:
        flash(message='通过申请', category='success')
        e.status = 1
        db.session.commit()
    return redirect(url_for('examine', conference_id=conference_id))


@app.route('/refuse_enroll/<conference_id>/<user_id>')
def refuse_enroll(conference_id, user_id):
    print('refuse_enroll conf:' + conference_id + ' user:' + user_id)
    e = Enroll.query.filter_by(user_id=user_id, conference_id=conference_id).first()
    if e is None:
        flash(message='Error', category='danger')
    else:
        flash(message='拒绝申请', category='info')
        e.status = 2
        db.session.commit()
    return redirect(url_for('examine', conference_id=conference_id))


# 文件上传相关
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 获取上传文件的url: file_url = url_for('uploaded_file', filename=filename)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return  send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/review/<conference_id>', methods=['GET', 'POST'])
@login_required
def review(conference_id):
    user = current_user
    tag = {'name': 'review'}
    conference = Conference.query.get(conference_id)
    if conference is None:
        flash(message='会议不存在!', category='danger')
        return redirect(url_for(previewlist))

    form = ReviewForm()
    if form.validate_on_submit():
        rev = form.review.data
        vid = form.vid.data
        conference.review = rev
        conference.vid = vid
        db.session.commit()
        flash(message='提交成功', category='success')

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash(message='本次提交未上传文件', category='info')
            return redirect(request.url)
        f = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if f.filename == '':
            flash(message='No selected file', category='danger')
        elif not allowed_file(f.filename):
            flash(message='不允许上传该格式文件', category='danger')
        elif f:
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename).replace('\\', '/'))
            file_url = 'https://dszdsz.cn/static' + url_for('uploaded_file', filename=filename)
            print(file_url)

            if Document.query.filter_by(filename=filename).first() is not None:
                flash(message='文件名重复', category='info')
            else:
                document = Document(filename=f.filename, url=file_url, conference_id=conference_id)
                db.session.add(document)
                db.session.commit()
                flash(message='文件上传成功', category='success')
        else:
            flash('文件上传失败', category='danger')

    docs = Document.query.filter_by(conference_id=conference.id)

    return render_template('review.html', user=user, tag=tag, conference=conference, docs=docs, form=form)


def get_conf_dict(conf, user):
    conf_dict = conf.to_dict()
    isJoin = False
    join_status = 0
    e = Enroll.query.filter_by(user_id=user.id, conference_id=conf.id).first()
    if e is not None:
        join_status = e.status
        isJoin = True
    conf_dict['join_status'] = join_status
    conf_dict['isJoin'] = isJoin
    conf_dict['num'] = conf.get_num()
    now = datetime.datetime.now()
    if now > conf.date + conf.duration:
        conf.status = '已结束'
        db.session.commit()
    return conf_dict


@app.route('/get_conferences', methods=['POST'])
def get_conferences():
    print(request.get_data())
    if not request.json or 'username' not in request.json:
        print('not json')
        abort(400)
    username = request.json['username']
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
    conferences = Conference.query.order_by(db.desc(Conference.id)).all()
    confs_dict = []
    for conf in conferences:
        conf_dict = get_conf_dict(conf, user)
        if conf_dict['status'] is not '未发布':
            confs_dict.append(conf_dict)
    print(confs_dict)
    return jsonify(confs_dict)


@app.route('/get_conference_detail', methods=['POST'])
def get_conference_detail():
    print(request.get_data())
    if not request.json or 'username' not in request.json:
        print('not json')
        abort(400)
    username = request.json['username']
    conference_id = request.json['conference_id']
    user = User.query.filter_by(username=username).first()
    conference = Conference.query.get(int(conference_id))
    if user is None or conference is None:
        return
    return jsonify(get_conf_dict(conference, user))


@app.route('/change_user_info', methods=['POST'])
def change_user_info():
    print(request.get_data())
    if not request.json or 'username' not in request.json:
        return "False"
    username = request.json['username']
    name = request.json['name']
    phone = request.json['phone']
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "False"
    user.name = name
    user.phone = phone
    db.session.commit()
    return "True"


@app.route('/enroll', methods=['POST'])
def enroll():
    print(request.get_data())
    if not request.json or 'username' not in request.json:
        return "False"
    user = User.query.filter_by(username=request.json['username']).first()
    conference = Conference.query.get(request.json['conference_id'])
    if user is None or conference is None:
        return "False"
    e = Enroll(time=datetime.datetime.today())
    e.conference = conference
    e.user_id = user.id
    if Enroll.query.filter_by(user_id=e.user_id, conference_id=e.conference_id).first() is not None:
        return "False"
    # user.enrolls.append(e)
    db.session.add(e)
    db.session.commit()
    return "True"


@app.route('/quit_enroll', methods=['POST'])
def quit_enroll():
    print(request.get_data())
    if not request.json or 'username' not in request.json:
        return "False"
    user = User.query.filter_by(username=request.json['username']).first()
    conf = Conference.query.get(request.json['conference_id'])
    if user is None or conf is None:
        return "False"
    e = Enroll.query.filter_by(user_id=user.id, conference_id=conf.id).first()
    if e is None:
        return "False"
    # user.enrolls.remove(e)
    db.session.delete(e)
    db.session.commit()
    return "True"


# 登录注册相关方法

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


# # 登录验证装饰器
# def login_required(func):
#     @wraps(func)
#     def decorated_function(*args, **kwargs):
#         if session.get('User'):  # 验证session
#             return func(*args, **kwargs)
#         else:
#             return redirect(url_for('login'))
#     return decorated_function


@app.before_request
def before_request():
    g.user = current_user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    tag = {'name': 'login'}
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username is "":
            flash(message='用户名不能为空', category='danger')
            return redirect(url_for('login'))
        elif password is "":
            flash(message='密码不能为空', category='danger')
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(message="账号不存在", category='danger')
            return redirect(url_for('login'))
        elif not user.check_pwd(password):
            flash(message='密码输入错误，请重新输入！', category='danger')
            return redirect(url_for('login'))
        session['user'] = username  # 匹配成功，添加session
        login_user(user, form.remember_me.data)
        flash(message='登录成功', category='success')
        return redirect(request.args.get('next') or url_for('index'))  # 重定向到首页
    return render_template('login.html', form=form, tag=tag)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(message='注销成功', category='success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    tag = {'name': 'register'}
    form = RegisterForm()
    print(form.validate())
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm = form.confirm.data
        name = form.name.data
        wechat = form.wechat.data

        user = User.query.filter_by(username=username).first()
        if len(username) < 6 or len(username) > 12:
            flash(message='用户名只能在6~12个字符之间', category='danger')
            return redirect(url_for('register'))
        elif len(password) < 6 or len(password) > 20:
            flash(message='密码只能在6~20个字符之间', category='danger')
            return redirect(url_for('register'))
        elif len(confirm)==0:
            flash(message='请确认密码', category='danger')
            return redirect(url_for('register'))
        elif len(name)==0:
            flash(message='输入真实姓名', category='danger')
            return redirect(url_for('register'))
        elif len(wechat)==0:
            flash(message='请输入微信号', category='danger')
            return redirect(url_for('register'))
        elif user:
            flash(message='用户名已存在，请重新输入', category='danger')
            return redirect(url_for('register'))
        elif password != confirm:
            flash(message='两次输入密码不一致，请重新输入', category='danger')
            return redirect(url_for('register'))

        user = User(username=form.username.data,
                    password=form.password.data,
                    name=form.name.data,
                    wechat=form.wechat.data,
                    is_super=1)
        db.session.add(user)
        db.session.commit()

        flash(message='注册成功', category='success')
        session['user'] = user.username  # 匹配成功，添加session
        login_user(user)
        return redirect(request.args.get('next') or url_for('index'))  # 重定向到首页
    return render_template('register.html', form=form, tag=tag)


# 发布会议
@app.route('/publish/<conference_id>', methods=['Get','POST'])
def publish(conference_id):
    conference = Conference.query.get(conference_id)
    if conference is None:
        flash(message='会议不存在!', category='danger')
    else:
        conference.status = '已发布'
        db.session.commit()
    return redirect(url_for('preview',conference_id=conference_id))
