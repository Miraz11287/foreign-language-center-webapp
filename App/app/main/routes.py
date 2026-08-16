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


@main_bp.route('/lessons/<int:lesson_id>/enroll', methods=['POST'])
def enroll(lesson_id):
    # Part 5: enrollment logic
    from flask import redirect, url_for, flash
    from flask_login import login_required
    week = request.form.get('week', '')
    flash('Enrollment coming in Part 5.', 'info')
    return redirect(url_for('main.schedule', week=week))


@main_bp.route('/lessons/<int:lesson_id>/unenroll', methods=['POST'])
def unenroll(lesson_id):
    from flask import redirect, url_for, flash
    week = request.form.get('week', '')
    flash('Unenrollment coming in Part 5.', 'info')
    return redirect(url_for('main.schedule', week=week))
