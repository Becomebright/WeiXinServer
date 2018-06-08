from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError

from app.models import User


class AddConferenceForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    date = DateTimeField('date', validators=[DataRequired()])
    place = StringField('place', validators=[DataRequired()])
    duration = StringField('duration', validators=[DataRequired()])
    introduction = StringField('introduction',validators=[DataRequired()])
    host = StringField('host',validators=[DataRequired()])
    guest_intro = StringField('guest_intro',validators=[DataRequired()])
    remark = StringField('remark',validators=[DataRequired()])

    submit = SubmitField('提交')


class LoginForm(FlaskForm):
    username = StringField(
        label='username',
    )
    password = PasswordField(
        label='password',
    )
    remember_me = BooleanField(
        'remember_me',
        default=False
    )
    submit = SubmitField(
        label='submit',
    )


# 用户注册表单
class RegisterForm(FlaskForm):
    username = StringField(
        label='用户名')
    password = PasswordField(
        label='密码')
    confirm = PasswordField(
        label='确认密码',)
    name = StringField(
        label='真实姓名')
    wechat = StringField(
        label='微信号')
    submit = SubmitField('立即注册')
