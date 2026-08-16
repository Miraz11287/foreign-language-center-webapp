from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User


class RegisterForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(2, 64)])
    last_name  = StringField('Last name',  validators=[DataRequired(), Length(2, 64)])
    email      = StringField('Email',      validators=[DataRequired(), Email()])
    password   = PasswordField('Password', validators=[DataRequired(), Length(6)])
    password2  = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit     = SubmitField('Create account')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('This email is already registered.')


class LoginForm(FlaskForm):
    email       = StringField('Email',    validators=[DataRequired(), Email()])
    password    = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit      = SubmitField('Log in')
