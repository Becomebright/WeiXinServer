# -*- coding: UTF-8 -*-

from app import db

# 用户user添加会议c：
# user.conferences.append(c)
# db.session.add(s)

# 用户user参加的会议:
# user.classes.all()

# 参加了会议c的用户:
# c.User.all()

# 用户user退选会议c:
# user.conferences.remove(c)


Enroll = db.Table(
    'Enroll',
    db.Column('user_id', db.Integer, db.ForeignKey('User.id')),
    db.Column('conference_id', db.Integer, db.ForeignKey('Conference.id'))
)


class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(64))
    is_super = db.Column(db.Boolean, default=False)

    manage_conferences = db.relationship('Conference', backref='admin')

    conferences = db.relationship(
        'Conference',
        secondary=Enroll,
        backref=db.backref('user', lazy='dynamic'),
        lazy='dynamic'
    )

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

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'password': self.password}


class Conference(db.Model):
    __tablename__ = 'Conference'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('User.id'))  # Who create this conference

    name = db.Column(db.String(64), index=True)
    date = db.Column(db.DateTime, index=True)
    place = db.Column(db.String(64), index=True)
    time = db.Column(db.Time)  # duration time
    status = db.Column(db.String(16))
    introduction = db.Column(db.String(1024))  # 会议介绍
    guest_intro = db.Column(db.String(1024))  # 嘉宾介绍
    remark = db.Column(db.String(128))  # 备注

    def __repr__(self):
        return '<Conference %r>' % self.name

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'date': self.date, 'place': self.place,
                'introduction': self.introduction}