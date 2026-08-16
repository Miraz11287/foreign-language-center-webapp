from datetime import datetime, timedelta, date
from flask import render_template, request
from flask_login import current_user
from app.main import main_bp
from app.extensions import db
from app.models.lesson import Lesson
from app.models.course import Course, LanguageLevel
from app.models.user import User, Role


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/schedule')
def schedule():
    # determine week start (Monday)
    week_str = request.args.get('week')
    try:
        week_start = datetime.strptime(week_str, '%Y-%m-%d').date()
        week_start -= timedelta(days=week_start.weekday())
    except (TypeError, ValueError):
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=7)

    # filters
    lang_filter    = request.args.get('language', '')
    level_filter   = request.args.get('level', '')
    teacher_filter = request.args.get('teacher_id', type=int)

    query = (
        Lesson.query
        .join(Course)
        .filter(
            Lesson.starts_at >= datetime.combine(week_start, datetime.min.time()),
            Lesson.starts_at <  datetime.combine(week_end,   datetime.min.time()),
        )
    )

    if lang_filter:
        query = query.filter(Course.language.ilike(f'%{lang_filter}%'))
    if level_filter:
        query = query.filter(Course.level == LanguageLevel(level_filter))
    if teacher_filter:
        query = query.filter(Lesson.teacher_id == teacher_filter)

    lessons = query.order_by(Lesson.starts_at).all()

    # group lessons by day
    days = {}
    for i in range(7):
        days[week_start + timedelta(days=i)] = []
    for lesson in lessons:
        day = lesson.starts_at.date()
        if day in days:
            days[day].append(lesson)

    # filter options
    languages = [
        r[0] for r in
        db.session.query(Course.language).distinct().order_by(Course.language).all()
    ]
    teachers = (
        User.query
        .filter(User.role.in_([Role.teacher, Role.admin]))
        .order_by(User.last_name)
        .all()
    )

    # enrolled lesson ids for the current student
    enrolled_ids = set()
    if current_user.is_authenticated and current_user.is_student():
        from app.models.enrollment import Enrollment, EnrollmentStatus
        enrolled_ids = {
            e.lesson_id for e in
            current_user.enrollments.filter_by(status=EnrollmentStatus.active).all()
        }

    return render_template(
        'schedule.html',
        days=days,
        week_start=week_start,
        today=date.today(),
        prev_week=(week_start - timedelta(days=7)).strftime('%Y-%m-%d'),
        next_week=(week_start + timedelta(days=7)).strftime('%Y-%m-%d'),
        languages=languages,
        teachers=teachers,
        levels=[l.value for l in LanguageLevel],
        selected_language=lang_filter,
        selected_level=level_filter,
        selected_teacher=teacher_filter,
        enrolled_ids=enrolled_ids,
    )


@main_bp.route('/request-teacher', methods=['GET', 'POST'])
def request_teacher():
    from flask import redirect, url_for, flash
    from flask_login import login_required, current_user
    from flask_wtf import FlaskForm
    from wtforms import TextAreaField, SubmitField
    from wtforms.validators import Optional
    from app.models.teacher_request import TeacherRequest, RequestStatus

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.is_teacher() or current_user.is_admin():
        flash('You already have teacher or admin access.', 'info')
        return redirect(url_for('main.index'))

    existing = current_user.teacher_requests.filter_by(
        status=RequestStatus.pending
    ).first()

    class RequestForm(FlaskForm):
        message = TextAreaField('Why do you want to become a teacher?', validators=[Optional()])
        submit  = SubmitField('Submit request')

    form = RequestForm()
    if form.validate_on_submit():
        if existing:
            flash('You already have a pending request.', 'info')
        else:
            req = TeacherRequest(user_id=current_user.id, message=form.message.data)
            db.session.add(req)
            db.session.commit()
            flash('Your request has been submitted. We will review it shortly.', 'success')
        return redirect(url_for('main.index'))

    return render_template('request_teacher.html', form=form, existing=existing)


@main_bp.route('/lessons/<int:lesson_id>/enroll', methods=['POST'])
def enroll(lesson_id):
    from flask import redirect, url_for, flash
    from flask_login import current_user
    from app.models.enrollment import Enrollment, EnrollmentStatus

    week = request.form.get('week', '')

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    lesson = db.session.get(Lesson, lesson_id)
    if not lesson:
        flash('Lesson not found.', 'error')
        return redirect(url_for('main.schedule', week=week))

    existing = Enrollment.query.filter_by(
        student_id=current_user.id, lesson_id=lesson_id
    ).first()

    if existing and existing.status == EnrollmentStatus.active:
        flash('You are already enrolled in this lesson.', 'info')
    elif lesson.is_full:
        flash('This lesson is full.', 'error')
    else:
        if existing:
            existing.status = EnrollmentStatus.active
        else:
            db.session.add(Enrollment(
                student_id=current_user.id,
                lesson_id=lesson_id,
            ))
        db.session.commit()
        flash(f'Enrolled in {lesson.course.name}.', 'success')

    return redirect(url_for('main.schedule', week=week))


@main_bp.route('/lessons/<int:lesson_id>/unenroll', methods=['POST'])
def unenroll(lesson_id):
    from flask import redirect, url_for, flash
    from flask_login import current_user
    from app.models.enrollment import Enrollment, EnrollmentStatus

    week = request.form.get('week', '')

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id,
        lesson_id=lesson_id,
        status=EnrollmentStatus.active,
    ).first()

    if enrollment:
        enrollment.status = EnrollmentStatus.cancelled
        db.session.commit()
        flash('Enrollment cancelled.', 'success')
    else:
        flash('No active enrollment found.', 'error')

    return redirect(url_for('main.schedule', week=week))


@main_bp.route('/my-lessons')
def my_lessons():
    from flask import redirect, url_for
    from flask_login import current_user
    from app.models.enrollment import Enrollment, EnrollmentStatus

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    enrollments = (
        Enrollment.query
        .filter_by(student_id=current_user.id, status=EnrollmentStatus.active)
        .join(Lesson)
        .order_by(Lesson.starts_at)
        .all()
    )
    return render_template('my_lessons.html', enrollments=enrollments)
