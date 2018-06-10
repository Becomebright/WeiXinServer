# -*- coding: UTF-8 -*-
import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = u"请先使用您的管理员账号登录"

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'doc', 'pptx', 'ppt', 'zip', 'rar', 'md'])
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 上传文件最大大小：8M


from app import views, models