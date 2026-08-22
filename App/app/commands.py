import click
from datetime import datetime, timezone, timedelta
from flask import current_app
from app.extensions import db
from app.models.user import User, Role
from app.models.course import Course, LanguageLevel
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.grade import Grade


def register_commands(app):
    @app.cli.command('seed')
    def seed():
        """Create demo users, courses and lessons."""

        # ── Users ──────────────────────────────────────────────────────────
        def make_user(first, last, email, password, role):
            if User.query.filter_by(email=email).first():
                return User.query.filter_by(email=email).first()
            u = User(first_name=first, last_name=last, email=email, role=role)
            u.set_password(password)
            db.session.add(u)
            return u

        admin   = make_user('Admin',  'LangCenter', 'admin@langcenter.com',   'admin123',   Role.admin)
        teacher = make_user('Sarah',  'Johnson',    'teacher@langcenter.com',  'teacher123', Role.teacher)
        student = make_user('Alex',   'Smith',      'student@langcenter.com',  'student123', Role.student)
        db.session.flush()

        # ── Courses ────────────────────────────────────────────────────────
        def make_course(name, language, level, description, teacher_id):
            if Course.query.filter_by(name=name).first():
                return Course.query.filter_by(name=name).first()
            c = Course(name=name, language=language, level=level,
                       description=description, teacher_id=teacher_id)
            db.session.add(c)
            return c

        eng_a1 = make_course(
            'English for Beginners', 'English', LanguageLevel.A1,
            'Perfect start for those with no prior English knowledge. '
            'We cover basic vocabulary, greetings, and simple sentences.',
            teacher.id)
        eng_b2 = make_course(
            'Business English', 'English', LanguageLevel.B2,
            'Develop professional communication skills: emails, negotiations, '
            'presentations, and business vocabulary.',
            teacher.id)
        fr_a2 = make_course(
            'French Essentials', 'French', LanguageLevel.A2,
            'Build on your basics with everyday French: shopping, travel, '
            'and simple conversations.',
            teacher.id)
        db.session.flush()

        # ── Lessons ────────────────────────────────────────────────────────
        now = datetime.now(timezone.utc)

        def make_lesson(course, delta_days, hour, room, capacity=12):
            starts = (now + timedelta(days=delta_days)).replace(
                hour=hour, minute=0, second=0, microsecond=0)
            if Lesson.query.filter_by(course_id=course.id, starts_at=starts).first():
                return Lesson.query.filter_by(course_id=course.id, starts_at=starts).first()
            l = Lesson(course_id=course.id, teacher_id=teacher.id,
                       starts_at=starts, duration_min=60, room=room, capacity=capacity)
            db.session.add(l)
            return l

        # Past lesson (so teacher can grade it)
        past = (now - timedelta(days=3)).replace(hour=10, minute=0, second=0, microsecond=0)
        past_lesson = Lesson.query.filter_by(course_id=eng_a1.id, starts_at=past).first()
        if not past_lesson:
            past_lesson = Lesson(course_id=eng_a1.id, teacher_id=teacher.id,
                                 starts_at=past, duration_min=60, room='101', capacity=12)
            db.session.add(past_lesson)

        l1 = make_lesson(eng_a1, 1,  10, '101')
        l2 = make_lesson(eng_a1, 3,  10, '101')
        l3 = make_lesson(eng_b2, 2,  14, '202')
        l4 = make_lesson(eng_b2, 5,  14, '202')
        l5 = make_lesson(fr_a2,  1,  16, '103')
        l6 = make_lesson(fr_a2,  4,  16, '103')
        db.session.flush()

        # ── Enroll student in past lesson + upcoming ────────────────────────
        def enroll(student_id, lesson):
            if Enrollment.query.filter_by(student_id=student_id, lesson_id=lesson.id).first():
                return
            db.session.add(Enrollment(
                student_id=student_id, lesson_id=lesson.id,
                status=EnrollmentStatus.active))

        enroll(student.id, past_lesson)
        enroll(student.id, l1)
        enroll(student.id, l3)
        db.session.flush()

        # ── Grade the past lesson ───────────────────────────────────────────
        if not Grade.query.filter_by(student_id=student.id, lesson_id=past_lesson.id).first():
            db.session.add(Grade(
                student_id=student.id, lesson_id=past_lesson.id,
                score=87.5, attended=True, notes='Good progress'))

        db.session.commit()
        click.echo('Seed complete.')
        click.echo('')
        click.echo('  Admin:   admin@langcenter.com   / admin123')
        click.echo('  Teacher: teacher@langcenter.com / teacher123')
        click.echo('  Student: student@langcenter.com / student123')
