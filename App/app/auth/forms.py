from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User, Role


class RegisterForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired(), Length(2, 64)])
    last_name  = StringField('Фамилия', validators=[DataRequired(), Length(2, 64)])
    email      = StringField('Email', validators=[DataRequired(), Email()])
    password   = PasswordField('Пароль', validators=[DataRequired(), Length(6)])
    password2  = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit     = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Этот email уже зарегистрирован.')


class LoginForm(FlaskForm):
    email       = StringField('Email', validators=[DataRequired(), Email()])
    password    = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit      = SubmitField('Войти')
