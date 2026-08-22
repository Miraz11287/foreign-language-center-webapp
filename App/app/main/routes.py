from datetime import datetime, timedelta, date
from flask import render_template, request
from flask_login import current_user
from app.main import main_bp
from app.extensions import db
from app.models.lesson import Lesson
from app.models.course import Course, LanguageLevel
from app.models.course_material import CourseMaterial
from app.models.course_rating import CourseRating
from app.models.course_comment import CourseComment
from app.models.user import User, Role


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/courses')
def courses():
    lang_filter  = request.args.get('language', '')
    level_filter = request.args.get('level', '')
    search_q     = request.args.get('q', '').strip()

    query = Course.query.filter_by(is_active=True)
    if lang_filter:
        query = query.filter(Course.language.ilike(f'%{lang_filter}%'))
    if level_filter:
        query = query.filter(Course.level == LanguageLevel(level_filter))
    if search_q:
        like = f'%{search_q}%'
        query = query.filter(
            db.or_(Course.name.ilike(like), Course.description.ilike(like))
        )

    all_courses = query.order_by(Course.language, Course.name).all()
    languages   = [r[0] for r in db.session.query(Course.language).distinct().order_by(Course.language).all()]
    levels      = [l.value for l in LanguageLevel]

    return render_template('courses.html',
        courses=all_courses,
        languages=languages,
        levels=levels,
        selected_language=lang_filter,
        selected_level=level_filter,
        search_q=search_q,
    )


@main_bp.route('/courses/<int:course_id>', methods=['GET', 'POST'])
def course_detail(course_id):
    from flask_login import current_user
    from flask import abort

    course = db.session.get(Course, course_id) or abort(404)

    # upcoming lessons
    upcoming = (
        course.lessons
        .filter(Lesson.starts_at >= datetime.now())
        .order_by(Lesson.starts_at)
        .limit(5)
        .all()
    )

    # user's existing rating
    user_rating = None
    if current_user.is_authenticated:
        r = CourseRating.query.filter_by(
            course_id=course_id, user_id=current_user.id
        ).first()
        user_rating = r.score if r else None

    comments = course.comments.all()
    materials = course.materials.all()

    return render_template('course_detail.html',
        course=course,
        upcoming=upcoming,
        user_rating=user_rating,
        comments=comments,
        materials=materials,
    )


@main_bp.route('/courses/<int:course_id>/rate', methods=['POST'])
def rate_course(course_id):
    from flask import redirect, url_for, flash
    from flask_login import current_user

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    score = request.form.get('score', type=int)
    if not score or not (1 <= score <= 5):
        flash('Invalid rating.', 'error')
        return redirect(url_for('main.course_detail', course_id=course_id))

    existing = CourseRating.query.filter_by(
        course_id=course_id, user_id=current_user.id
    ).first()

    if existing:
        existing.score = score
    else:
        db.session.add(CourseRating(
            course_id=course_id, user_id=current_user.id, score=score
        ))
    db.session.commit()
    flash('Rating saved.', 'success')
    return redirect(url_for('main.course_detail', course_id=course_id))


@main_bp.route('/courses/<int:course_id>/comment', methods=['POST'])
def comment_course(course_id):
    from flask import redirect, url_for, flash
    from flask_login import current_user

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    body = request.form.get('body', '').strip()
    if not body:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('main.course_detail', course_id=course_id))

    db.session.add(CourseComment(
        course_id=course_id, user_id=current_user.id, body=body
    ))
    db.session.commit()
    flash('Comment added.', 'success')
    return redirect(url_for('main.course_detail', course_id=course_id))


@main_bp.route('/courses/<int:course_id>/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(course_id, comment_id):
    from flask import redirect, url_for, flash, abort
    from flask_login import current_user

    comment = db.session.get(CourseComment, comment_id) or abort(404)
    if comment.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect(url_for('main.course_detail', course_id=course_id))


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4'}
UPLOAD_FOLDER = '/app/uploads/materials'


def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main_bp.route('/courses/<int:course_id>/materials/new', methods=['GET', 'POST'])
def material_new(course_id):
    import os, uuid
    from flask import redirect, url_for, flash, abort
    from flask_login import current_user
    from flask_wtf import FlaskForm
    from flask_wtf.file import FileField, FileAllowed
    from wtforms import StringField, TextAreaField, SubmitField
    from wtforms.validators import DataRequired, Optional

    course = db.session.get(Course, course_id) or abort(404)
    can_edit = (
        current_user.is_authenticated and
        (current_user.is_admin() or course.teacher_id == current_user.id)
    )
    if not can_edit:
        abort(403)

    class MaterialForm(FlaskForm):
        title   = StringField('Title', validators=[DataRequired()])
        content = TextAreaField('Content', validators=[Optional()])
        file    = FileField('Attach file (PDF, DOCX, image…)',
                            validators=[FileAllowed(list(ALLOWED_EXTENSIONS), 'File type not allowed.')])
        submit  = SubmitField('Save')

    form = MaterialForm()
    if form.validate_on_submit():
        saved_name = saved_path = None
        f = form.file.data
        if f and f.filename:
            if not _allowed(f.filename):
                flash('File type not allowed.', 'error')
                return render_template('material_form.html', form=form, course=course, title='New material')
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            ext = f.filename.rsplit('.', 1)[1].lower()
            saved_name = f.filename
            unique_name = f'{uuid.uuid4().hex}.{ext}'
            saved_path = os.path.join(UPLOAD_FOLDER, unique_name)
            f.save(saved_path)

        order = course.materials.count()
        db.session.add(CourseMaterial(
            course_id=course_id,
            author_id=current_user.id,
            title=form.title.data.strip(),
            content=form.content.data.strip() if form.content.data else None,
            order=order,
            file_name=saved_name,
            file_path=saved_path,
        ))
        db.session.commit()
        flash('Material added.', 'success')
        return redirect(url_for('main.course_detail', course_id=course_id))

    return render_template('material_form.html', form=form, course=course, title='New material')


@main_bp.route('/courses/<int:course_id>/materials/<int:material_id>/download')
def material_download(course_id, material_id):
    import os
    from flask import send_file, abort
    from flask_login import current_user

    material = db.session.get(CourseMaterial, material_id) or abort(404)
    if not material.file_path or not os.path.exists(material.file_path):
        abort(404)
    return send_file(material.file_path, as_attachment=True, download_name=material.file_name)


@main_bp.route('/courses/<int:course_id>/materials/<int:material_id>/edit', methods=['GET', 'POST'])
def material_edit(course_id, material_id):
    import os, uuid
    from flask import redirect, url_for, flash, abort
    from flask_login import current_user
    from flask_wtf import FlaskForm
    from flask_wtf.file import FileField, FileAllowed
    from wtforms import StringField, TextAreaField, SubmitField, BooleanField
    from wtforms.validators import DataRequired, Optional

    material = db.session.get(CourseMaterial, material_id) or abort(404)
    course   = db.session.get(Course, course_id) or abort(404)
    can_edit = (
        current_user.is_authenticated and
        (current_user.is_admin() or course.teacher_id == current_user.id)
    )
    if not can_edit:
        abort(403)

    class MaterialForm(FlaskForm):
        title        = StringField('Title', validators=[DataRequired()])
        content      = TextAreaField('Content', validators=[Optional()])
        file         = FileField('Replace file',
                                 validators=[FileAllowed(list(ALLOWED_EXTENSIONS), 'File type not allowed.')])
        remove_file  = BooleanField('Remove current file')
        submit       = SubmitField('Save')

    form = MaterialForm(obj=material)

    if form.validate_on_submit():
        material.title   = form.title.data.strip()
        material.content = form.content.data.strip() if form.content.data else None

        f = form.file.data
        if f and f.filename:
            # replace file: delete old, save new
            if material.file_path and os.path.exists(material.file_path):
                os.remove(material.file_path)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            ext = f.filename.rsplit('.', 1)[1].lower()
            unique_name = f'{uuid.uuid4().hex}.{ext}'
            saved_path = os.path.join(UPLOAD_FOLDER, unique_name)
            f.save(saved_path)
            material.file_name = f.filename
            material.file_path = saved_path
        elif form.remove_file.data and material.file_path:
            if os.path.exists(material.file_path):
                os.remove(material.file_path)
            material.file_name = None
            material.file_path = None

        db.session.commit()
        flash('Material updated.', 'success')
        return redirect(url_for('main.course_detail', course_id=course_id))

    return render_template('material_form.html', form=form, course=course,
                           title='Edit material', material=material)


@main_bp.route('/courses/<int:course_id>/materials/<int:material_id>/delete', methods=['POST'])
def material_delete(course_id, material_id):
    import os
    from flask import redirect, url_for, flash, abort
    from flask_login import current_user

    material = db.session.get(CourseMaterial, material_id) or abort(404)
    course   = db.session.get(Course, course_id) or abort(404)
    can_edit = (
        current_user.is_authenticated and
        (current_user.is_admin() or course.teacher_id == current_user.id)
    )
    if not can_edit:
        abort(403)
    if material.file_path and os.path.exists(material.file_path):
        os.remove(material.file_path)
    db.session.delete(material)
    db.session.commit()
    flash('Material deleted.', 'success')
    return redirect(url_for('main.course_detail', course_id=course_id))


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


@main_bp.route('/my-progress')
def my_progress():
    from flask import redirect, url_for
    from flask_login import current_user
    from app.models.grade import Grade
    from app.models.enrollment import Enrollment, EnrollmentStatus

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    grades = (
        Grade.query
        .filter_by(student_id=current_user.id)
        .join(Lesson)
        .order_by(Lesson.starts_at.desc())
        .all()
    )

    # stats
    attended = sum(1 for g in grades if g.attended)
    scored   = [g.score for g in grades if g.score is not None]
    avg      = round(sum(scored) / len(scored), 1) if scored else None

    return render_template('my_progress.html',
        grades=grades,
        total=len(grades),
        attended=attended,
        avg=avg,
    )


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
