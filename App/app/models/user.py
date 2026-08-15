import enum
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class Role(enum.Enum):
    admin = 'admin'
    teacher = 'teacher'
    student = 'student'


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.student)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    taught_courses = db.relationship('Course', back_populates='teacher', lazy='dynamic')
    taught_lessons = db.relationship('Lesson', back_populates='teacher', lazy='dynamic')
    enrollments = db.relationship('Enrollment', back_populates='student', lazy='dynamic')
    grades = db.relationship('Grade', back_populates='student', lazy='dynamic')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def is_admin(self) -> bool:
        return self.role == Role.admin

    def is_teacher(self) -> bool:
        return self.role == Role.teacher

    def is_student(self) -> bool:
        return self.role == Role.student

    def __repr__(self) -> str:
        return f'<User {self.email} [{self.role.value}]>'
