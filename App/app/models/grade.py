from datetime import datetime, timezone
from app.extensions import db


class Grade(db.Model):
    __tablename__ = 'grades'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'lesson_id', name='uq_grade_student_lesson'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    score = db.Column(db.Float)           # 0.0–100.0, None = ещё не выставлена
    attended = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)
    graded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    student = db.relationship('User', back_populates='grades')
    lesson = db.relationship('Lesson', back_populates='grades')

    def __repr__(self) -> str:
        return f'<Grade student={self.student_id} lesson={self.lesson_id} score={self.score}>'
