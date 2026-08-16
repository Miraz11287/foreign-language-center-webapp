from datetime import datetime, timezone
from app.extensions import db


class CourseComment(db.Model):
    __tablename__ = 'course_comments'

    id        = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    body      = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    course = db.relationship('Course', back_populates='comments')
    user   = db.relationship('User')
