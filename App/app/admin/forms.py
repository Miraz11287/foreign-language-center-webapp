from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, IntegerField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from app.models.course import LanguageLevel


class CourseForm(FlaskForm):
    name        = StringField('Course name', validators=[DataRequired(), Length(2, 128)])
    language    = StringField('Language',    validators=[DataRequired(), Length(2, 64)])
    level       = SelectField('Level',       choices=[(l.value, l.value) for l in LanguageLevel])
    description = TextAreaField('Description', validators=[Optional()])
    teacher_id  = SelectField('Teacher',     coerce=int)
    submit      = SubmitField('Save')


class LessonForm(FlaskForm):
    course_id    = SelectField('Course',           coerce=int, validators=[DataRequired()])
    teacher_id   = SelectField('Teacher',          coerce=int, validators=[DataRequired()])
    starts_at    = DateTimeLocalField('Date & time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    duration_min = IntegerField('Duration (min)',   default=60, validators=[NumberRange(min=15, max=480)])
    room         = StringField('Room',             validators=[Optional(), Length(max=32)])
    capacity     = IntegerField('Capacity',        default=10, validators=[NumberRange(min=1, max=100)])
    submit       = SubmitField('Save')


class UserRoleForm(FlaskForm):
    role   = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')])
    submit = SubmitField('Change')
