import enum
from datetime import datetime, timezone
from app.extensions import db


class EnrollmentStatus(enum.Enum):
    active = 'active'
    cancelled = 'cancelled'


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'lesson_id', name='uq_student_lesson'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    status = db.Column(
        db.Enum(EnrollmentStatus),
        nullable=False,
        default=EnrollmentStatus.active,
    )
    enrolled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship('User', back_populates='enrollments')
    lesson = db.relationship('Lesson', back_populates='enrollments')

    def __repr__(self) -> str:
        return f'<Enrollment student={self.student_id} lesson={self.lesson_id} [{self.status.value}]>'
