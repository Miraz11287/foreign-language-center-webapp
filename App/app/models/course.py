import enum
from datetime import datetime, timezone
from app.extensions import db


class LanguageLevel(enum.Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    language = db.Column(db.String(64), nullable=False)   # 'Английский', 'Немецкий', ...
    level = db.Column(db.Enum(LanguageLevel), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    teacher = db.relationship('User', back_populates='taught_courses')
    lessons = db.relationship('Lesson', back_populates='course', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<Course {self.name} [{self.language} {self.level.value}]>'
