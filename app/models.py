# -*- coding: UTF-8 -*-
from flask import session

from app import db

# 用户user添加会议c：
# user = User.query.get(1)
# e = Enroll(time=datetime.today())
# e.conference = conference
# user.enrolls.append(e)
# db.session.add(e)
# db.session.commit()

# 用户user取消报名会议conf：
# e = Enroll.query.filter_by(user_id=user.id, conference_id=conf.id)
# user.enrolls.remove(e)
# db.session.delete(e)
# db.session.commit()

# 用户user参加的会议:
# user.conferences.all()

# 参加了会议c的用户:
#session.query(User).filter(User.conferences.any(id=xxx)).all()

# 用户user退选会议c:
# user.conferences.remove(c)


# Enroll = db.Table(
#     'Enroll',
#     db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
#     db.Column('conference_id', db.Integer, db.ForeignKey('Conference.id')),
#     db.Column('time', db.DateTime),
#     db.Column('status', db.Integer)  # 报名状态：0-审核中, 1-审核通过
# )


class Enroll (db.Model):
    __tablename__ = 'Enroll'
    user_id = db.Column(db.Integer,db.ForeignKey('User.id'), primary_key=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('Conference.id'), primary_key=True)
    time = db.Column(db.DateTime),
    status = db.Column(db.Integer, default=0)  # 报名状态：0-审核中, 1-审核通过, 2-审核不通过
    conference = db.relationship("Conference", backref="enroll")


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

    enrolls = db.relationship(
        'Enroll',
        backref='user',
        lazy='dynamic',
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
            confs = []
            enrolls = Enroll.query.filter_by(user_id=self.id).all()
            for e in enrolls:
                c = Conference.query.get(e.conference_id)
                confs.append(c.to_dict())
            ret_dict['conferences'] = confs
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
    image = db.Column(db.String(128))                   # 海报url
    vid = db.Column(db.String(32))                      # 视频vid
    review = db.Column(db.String(1024))                 # 会议回顾

    documents = db.relationship('Document', backref='conference', lazy='dynamic')	# 会议文件


    # users = db.relationship(
    #     'Enroll',
    #     secondary=Enroll,
    #     backref=db.backref('conference', lazy='dynamic'),
    #     lazy='dynamic'
    # )

    def __repr__(self):
        return '<Conference %r>' % self.name

    def to_dict(self):
        docoments_dict = []
        for doc in self.documents:
            docoments_dict.append(doc.to_dict())
        return {
            'id': self.id,
            'name': self.name,
            'date': str(self.date),
            'duration': str(self.duration),
            'place': self.place,
            'introduction': self.introduction,
            'host': self.host,
            'guest_intro': self.guest_intro,
            'remark': self.remark,
            'status': self.status,
            'create_time': self.create_time,
            'files': docoments_dict,
            'image': self.image,
            'vid': self.vid,
            'review': self.review
        }

    # 获取会议结束时间
    def get_end_time(self):
        return self.date + self.duration

    # 获取会议参加人数
    def get_num(self):
        return len(Enroll.query.filter_by(conference_id=self.id).all())


class Document(db.Model):
    __tablename__ = 'Document'

    id = db.Column(db.Integer, primary_key=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('Conference.id'))

    filename = db.Column(db.String(64), unique=True)
    url = db.Column(db.String(256))

    def __repr__(self):
        return '<Document %r>' % self.id

    def to_dict(self):
        return {'id': self.id, 'conference_id': self.conference_id, 'url': self.url, 'filename': self.filename}

