from datetime import datetime, timezone
from app.extensions import db


class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    duration_min = db.Column(db.Integer, nullable=False, default=60)
    room = db.Column(db.String(32))
    capacity = db.Column(db.Integer, nullable=False, default=10)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    course = db.relationship('Course', back_populates='lessons')
    teacher = db.relationship('User', back_populates='taught_lessons')
    enrollments = db.relationship('Enrollment', back_populates='lesson', lazy='dynamic')
    grades = db.relationship('Grade', back_populates='lesson', lazy='dynamic')

    @property
    def enrolled_count(self) -> int:
        return self.enrollments.filter_by(status='active').count()

    @property
    def is_full(self) -> bool:
        return self.enrolled_count >= self.capacity

    def __repr__(self) -> str:
        return f'<Lesson course={self.course_id} @ {self.starts_at}>'
