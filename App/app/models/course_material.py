from datetime import datetime, timezone
from app.extensions import db


class CourseMaterial(db.Model):
    __tablename__ = 'course_materials'

    id        = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    title     = db.Column(db.String(200), nullable=False)
    content   = db.Column(db.Text, nullable=True)
    order     = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # file attachment (optional)
    file_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)

    course = db.relationship('Course', back_populates='materials')
    author = db.relationship('User')
