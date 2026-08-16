import enum
from datetime import datetime, timezone
from app.extensions import db


class RequestStatus(enum.Enum):
    pending  = 'pending'
    approved = 'approved'
    rejected = 'rejected'


class TeacherRequest(db.Model):
    __tablename__ = 'teacher_requests'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message    = db.Column(db.Text)
    status     = db.Column(db.Enum(RequestStatus), nullable=False, default=RequestStatus.pending)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('teacher_requests', lazy='dynamic'))

    def __repr__(self):
        return f'<TeacherRequest user={self.user_id} [{self.status.value}]>'
