from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    login = StringField('Логин пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль пользователя', validators=[DataRequired()])
    submit = SubmitField('Авторизоваться в системе')
