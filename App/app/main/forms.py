from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Optional

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}


class MaterialForm(FlaskForm):
    title       = StringField('Title', validators=[DataRequired()])
    content     = TextAreaField('Content', validators=[Optional()])
    file        = FileField('Attach file (PDF, DOCX, image…)',
                            validators=[FileAllowed(list(ALLOWED_EXTENSIONS), 'File type not allowed.')])
    remove_file = BooleanField('Remove current file')
    submit      = SubmitField('Save')
