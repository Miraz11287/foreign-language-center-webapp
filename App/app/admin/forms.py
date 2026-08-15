from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, IntegerField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from app.models.course import LanguageLevel


class CourseForm(FlaskForm):
    name        = StringField('Название курса', validators=[DataRequired(), Length(2, 128)])
    language    = StringField('Язык', validators=[DataRequired(), Length(2, 64)])
    level       = SelectField('Уровень', choices=[(l.value, l.value) for l in LanguageLevel])
    description = TextAreaField('Описание', validators=[Optional()])
    teacher_id  = SelectField('Преподаватель', coerce=int)
    submit      = SubmitField('Сохранить')


class LessonForm(FlaskForm):
    course_id    = SelectField('Курс', coerce=int, validators=[DataRequired()])
    teacher_id   = SelectField('Преподаватель', coerce=int, validators=[DataRequired()])
    starts_at    = DateTimeLocalField('Дата и время', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    duration_min = IntegerField('Длительность (мин)', default=60, validators=[NumberRange(min=15, max=480)])
    room         = StringField('Аудитория', validators=[Optional(), Length(max=32)])
    capacity     = IntegerField('Количество мест', default=10, validators=[NumberRange(min=1, max=100)])
    submit       = SubmitField('Сохранить')


class UserRoleForm(FlaskForm):
    role   = SelectField('Роль', choices=[('student', 'Студент'), ('teacher', 'Преподаватель'), ('admin', 'Администратор')])
    submit = SubmitField('Изменить')
