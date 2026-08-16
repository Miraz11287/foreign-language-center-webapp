from flask import Blueprint

teacher_bp = Blueprint('teacher', __name__)

from app.teacher import routes  # noqa: F401, E402
