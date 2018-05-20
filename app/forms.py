from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField, DecimalField
from wtforms.validators import DataRequired


class AddConferenceForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    date = DateTimeField('date', validators=[DataRequired()])
    place = StringField('place', validators=[DataRequired()])

    submit = SubmitField('submit')


class LoginForm(FlaskForm):
    username = StringField(
        label='username',
        validators=[DataRequired('请输入用户名')],
        description="用户名",
        render_kw={
            "class":"form-control",
            "placeholder":"请输入账号!",
            "required":'required'               #表示输入框不能为空，并有提示信息
        }
    )
    password = PasswordField(
        label='password',
        validators=[DataRequired('请输入密码')],
        description='密码',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码!",
            "required": 'required'  # 表示输入框不能为空
        }
    )
    remember_me = BooleanField(
        'remember_me',
        default=False
    )

    submit = SubmitField(
        label='submit',
        render_kw={
            'class': 'btn btn-primary'
        }
    )