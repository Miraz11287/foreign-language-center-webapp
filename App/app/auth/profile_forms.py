from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class EditProfileForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(2, 64)])
    last_name  = StringField('Last name',  validators=[DataRequired(), Length(2, 64)])
    submit     = SubmitField('Save changes')


class ChangePasswordForm(FlaskForm):
    current    = PasswordField('Current password', validators=[DataRequired()])
    new_pass   = PasswordField('New password',     validators=[DataRequired(), Length(6)])
    confirm    = PasswordField('Confirm new password', validators=[DataRequired(), EqualTo('new_pass')])
    submit     = SubmitField('Change password')
