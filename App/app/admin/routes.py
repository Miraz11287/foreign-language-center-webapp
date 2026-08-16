from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from app.admin import admin_bp
from app.admin.forms import CourseForm, LessonForm, UserRoleForm
from app.auth.decorators import admin_required
from app.extensions import db
from app.models.user import User, Role
from app.models.course import Course, LanguageLevel
from app.models.lesson import Lesson
from app.models.teacher_request import TeacherRequest, RequestStatus


def _teacher_choices():
    teachers = User.query.filter(
        User.role.in_([Role.teacher, Role.admin])
    ).order_by(User.last_name).all()
    return [(t.id, t.full_name) for t in teachers]


def _course_choices():
    courses = Course.query.filter_by(is_active=True).order_by(Course.name).all()
    return [(c.id, f'{c.name} ({c.language} {c.level.value})') for c in courses]


# ─── Dashboard ───────────────────────────────────────────────────────────────

@admin_bp.route('/')
@login_required
@admin_required
def index():
    stats = {
        'users':    User.query.count(),
        'courses':  Course.query.count(),
        'lessons':  Lesson.query.count(),
        'requests': TeacherRequest.query.filter_by(status=RequestStatus.pending).count(),
    }
    return render_template('admin/index.html', stats=stats)


# ─── Teacher requests ─────────────────────────────────────────────────────────

@admin_bp.route('/requests')
@login_required
@admin_required
def teacher_requests():
    requests = TeacherRequest.query.order_by(TeacherRequest.created_at.desc()).all()
    return render_template('admin/teacher_requests.html', requests=requests)


@admin_bp.route('/requests/<int:req_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_request(req_id):
    from datetime import datetime, timezone
    req = db.session.get(TeacherRequest, req_id) or abort(404)
    req.status = RequestStatus.approved
    req.reviewed_at = datetime.now(timezone.utc)
    req.user.role = Role.teacher
    db.session.commit()
    from app.notifications.utils import notify
    notify(req.user_id, 'Your teacher request has been approved! You now have teacher access.', '/teacher/')
    flash(f'{req.user.full_name} is now a teacher.', 'success')
    return redirect(url_for('admin.teacher_requests'))


@admin_bp.route('/requests/<int:req_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_request(req_id):
    from datetime import datetime, timezone
    req = db.session.get(TeacherRequest, req_id) or abort(404)
    req.status = RequestStatus.rejected
    req.reviewed_at = datetime.now(timezone.utc)
    db.session.commit()
    from app.notifications.utils import notify
    notify(req.user_id, 'Your teacher request has been reviewed and was not approved.')
    flash(f'Request from {req.user.full_name} rejected.', 'success')
    return redirect(url_for('admin.teacher_requests'))


# ─── Users ───────────────────────────────────────────────────────────────────

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.last_name).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def change_role(user_id):
    user = db.session.get(User, user_id) or abort(404)
    role_value = request.form.get('role')
    try:
        user.role = Role[role_value]
        db.session.commit()
        flash(f'Role updated for {user.full_name}.', 'success')
    except KeyError:
        flash('Invalid role.', 'error')
    return redirect(url_for('admin.users'))


# ─── Courses ─────────────────────────────────────────────────────────────────

@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    all_courses = Course.query.order_by(Course.language, Course.name).all()
    return render_template('admin/courses.html', courses=all_courses)


@admin_bp.route('/courses/new', methods=['GET', 'POST'])
@login_required
@admin_required
def course_new():
    form = CourseForm()
    form.teacher_id.choices = _teacher_choices()
    if form.validate_on_submit():
        course = Course(
            name=form.name.data.strip(),
            language=form.language.data.strip(),
            level=LanguageLevel(form.level.data),
            description=form.description.data,
            teacher_id=form.teacher_id.data,
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created.', 'success')
        return redirect(url_for('admin.courses'))
    return render_template('admin/course_form.html', form=form, title='New course')


@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def course_edit(course_id):
    course = db.session.get(Course, course_id) or abort(404)
    form = CourseForm(obj=course)
    form.teacher_id.choices = _teacher_choices()
    if form.validate_on_submit():
        course.name        = form.name.data.strip()
        course.language    = form.language.data.strip()
        course.level       = LanguageLevel(form.level.data)
        course.description = form.description.data
        course.teacher_id  = form.teacher_id.data
        db.session.commit()
        flash('Course updated.', 'success')
        return redirect(url_for('admin.courses'))
    form.level.data = course.level.value
    return render_template('admin/course_form.html', form=form, title='Edit course')


@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def course_delete(course_id):
    course = db.session.get(Course, course_id) or abort(404)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'success')
    return redirect(url_for('admin.courses'))


# ─── Lessons ─────────────────────────────────────────────────────────────────

@admin_bp.route('/lessons')
@login_required
@admin_required
def lessons():
    all_lessons = Lesson.query.order_by(Lesson.starts_at).all()
    return render_template('admin/lessons.html', lessons=all_lessons)


@admin_bp.route('/lessons/new', methods=['GET', 'POST'])
@login_required
@admin_required
def lesson_new():
    form = LessonForm()
    form.course_id.choices  = _course_choices()
    form.teacher_id.choices = _teacher_choices()
    if form.validate_on_submit():
        lesson = Lesson(
            course_id=form.course_id.data,
            teacher_id=form.teacher_id.data,
            starts_at=form.starts_at.data,
            duration_min=form.duration_min.data,
            room=form.room.data,
            capacity=form.capacity.data,
        )
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson added.', 'success')
        return redirect(url_for('admin.lessons'))
    return render_template('admin/lesson_form.html', form=form, title='New lesson')


@admin_bp.route('/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def lesson_edit(lesson_id):
    lesson = db.session.get(Lesson, lesson_id) or abort(404)
    form = LessonForm(obj=lesson)
    form.course_id.choices  = _course_choices()
    form.teacher_id.choices = _teacher_choices()
    if form.validate_on_submit():
        lesson.course_id    = form.course_id.data
        lesson.teacher_id   = form.teacher_id.data
        lesson.starts_at    = form.starts_at.data
        lesson.duration_min = form.duration_min.data
        lesson.room         = form.room.data
        lesson.capacity     = form.capacity.data
        db.session.commit()
        flash('Lesson updated.', 'success')
        return redirect(url_for('admin.lessons'))
    return render_template('admin/lesson_form.html', form=form, title='Edit lesson')


@admin_bp.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
@admin_required
def lesson_delete(lesson_id):
    lesson = db.session.get(Lesson, lesson_id) or abort(404)
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted.', 'success')
    return redirect(url_for('admin.lessons'))
