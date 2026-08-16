from datetime import datetime, timezone
from app.extensions import db


class CourseRating(db.Model):
    __tablename__ = 'course_ratings'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'course_id', name='uq_user_course_rating'),
    )

    id        = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    score     = db.Column(db.Integer, nullable=False)              # 1–5
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    course = db.relationship('Course', back_populates='ratings')
    user   = db.relationship('User')
