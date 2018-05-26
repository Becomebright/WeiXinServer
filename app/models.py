# -*- coding: UTF-8 -*-

from app import db

# 用户user添加会议c：
# user.conferences.append(c)
# db.session.add(s)

# 用户user参加的会议:
# user.conferences.all()

# 参加了会议c的用户:
# c.User.all()

# 用户user退选会议c:
# user.conferences.remove(c)


Enroll = db.Table(
    'Enroll',
    db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
    db.Column('conference_id', db.Integer, db.ForeignKey('Conference.id')),
    db.Column('time', db.DateTime),
    db.Column('status', db.Integer)  # 报名状态：0-审核中, 1-审核通过
)


class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)                        # id
    username = db.Column(db.String(64), index=True, unique=True)        # 用户名
    password = db.Column(db.String(64))                                 # 密码
    wechat = db.Column(db.String(64), unique=True)                      # 微信号
    phone = db.Column(db.String(20), unique=True)                       # 手机号
    wechat_nickname = db.Column(db.String(64))                          # 微信昵称
    name = db.Column(db.String(32))                                     # 真实姓名
    sex = db.Column(db.Integer, index=True, default=0)                  # 性别, 0为男，1为女
    is_super = db.Column(db.Integer, default=0)                         # 管理员权限, 1为管理员

    manage_conferences = db.relationship('Conference', backref='admin', lazy='dynamic')

    conferences = db.relationship(
        'Conference',
        secondary=Enroll,
        backref=db.backref('user', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        ret_dict = {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'wechat': self.wechat,
            'phone': self.phone,
            'wechat_nickname': self.wechat_nickname,
            'name': self.name,
            'sex': self.sex,
            'is_super': self.is_super
        }
        if self.is_super is True:
            ret_dict['manage_conferences'] = self.manage_conferences
        else:
            ret_dict['conferences'] = self.conferences
        return ret_dict


    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    # 定义密码验证函数
    def check_pwd(self, pwd):
        return pwd == self.password

    def get_id(self):
        return str(self.id)  # python 3


class Conference(db.Model):
    __tablename__ = 'Conference'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('User.id'))  # Who create this conference

    name = db.Column(db.String(64), index=True)     	# 会议名称
    date = db.Column(db.DateTime, index=True)       	# 会议开始时间
    duration = db.Column(db.Interval)                   # 会议持续时间
    place = db.Column(db.String(64))    	            # 会议地点
    introduction = db.Column(db.String(1024))       	# 会议简介
    host = db.Column(db.String(32))                 	# 会议主持人
    guest_intro = db.Column(db.String(1024))        	# 嘉宾介绍
    remark = db.Column(db.String(128))              	# 会议备注
    status = db.Column(db.String(16))               	# 会议状态
    create_time = db.Column(db.DateTime, index=True)	# 会议发布时间
    documents = db.relationship('Document', backref='conference', lazy='dynamic')	# 会议文件

    def __repr__(self):
        return '<Conference %r>' % self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'duration': self.duration,
            'place': self.place,
            'introduction': self.introduction,
            'host': self.host,
            'guest_intro': self.guest_intro,
            'remark': self.remark,
            'status': self.status,
            'create_time': self.get_end_time(),
            'documents': self.documents
        }

    # 获取会议结束时间
    def get_end_time(self):
        return self.date + self.duration


class Document(db.Model):
    __tablename__ = 'Document'

    id = db.Column(db.Integer, primary_key=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('Conference.id'))

    url = db.Column(db.String(512))

    def __repr__(self):
        return '<Document %r>' % self.id

    def to_dict(self):
        return {'id': self.id, 'conference_id': self.conference_id, 'url': self.url}