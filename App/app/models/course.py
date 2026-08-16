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

    teacher   = db.relationship('User', back_populates='taught_courses')
    lessons   = db.relationship('Lesson', back_populates='course', lazy='dynamic')
    materials = db.relationship('CourseMaterial', back_populates='course',
                                order_by='CourseMaterial.order', lazy='dynamic')
    ratings   = db.relationship('CourseRating',  back_populates='course', lazy='dynamic')
    comments  = db.relationship('CourseComment', back_populates='course',
                                order_by='CourseComment.created_at.desc()', lazy='dynamic')

    @property
    def avg_rating(self):
        from sqlalchemy import func
        from app.extensions import db as _db
        result = _db.session.query(func.avg(CourseRating.score)).filter_by(course_id=self.id).scalar()
        return round(float(result), 1) if result else None

    @property
    def rating_count(self):
        return self.ratings.count()

    def __repr__(self) -> str:
        return f'<Course {self.name} [{self.language} {self.level.value}]>'


from app.models.course_rating import CourseRating  # noqa: E402 (avoid circular at top)
