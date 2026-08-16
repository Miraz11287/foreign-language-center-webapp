from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.teacher import teacher_bp
from app.auth.decorators import teacher_required
from app.extensions import db
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.grade import Grade


@teacher_bp.route('/')
@login_required
@teacher_required
def index():
    lessons = (
        Lesson.query
        .filter_by(teacher_id=current_user.id)
        .order_by(Lesson.starts_at.desc())
        .all()
    )
    return render_template('teacher/index.html', lessons=lessons)


@teacher_bp.route('/lessons/<int:lesson_id>/grades', methods=['GET', 'POST'])
@login_required
@teacher_required
def grade_lesson(lesson_id):
    lesson = db.session.get(Lesson, lesson_id) or abort(404)

    if lesson.teacher_id != current_user.id and not current_user.is_admin():
        abort(403)

    enrollments = (
        Enrollment.query
        .filter_by(lesson_id=lesson_id, status=EnrollmentStatus.active)
        .all()
    )

    if request.method == 'POST':
        for enrollment in enrollments:
            sid = enrollment.student_id
            score_raw = request.form.get(f'score_{sid}', '').strip()
            attended  = bool(request.form.get(f'attended_{sid}'))
            notes     = request.form.get(f'notes_{sid}', '').strip()

            score = float(score_raw) if score_raw else None

            grade = Grade.query.filter_by(
                student_id=sid, lesson_id=lesson_id
            ).first()

            if grade:
                grade.score    = score
                grade.attended = attended
                grade.notes    = notes
            else:
                db.session.add(Grade(
                    student_id=sid,
                    lesson_id=lesson_id,
                    score=score,
                    attended=attended,
                    notes=notes,
                ))

        db.session.commit()
        flash('Grades saved.', 'success')
        return redirect(url_for('teacher.grade_lesson', lesson_id=lesson_id))

    # load existing grades into a dict for the template
    existing = {
        g.student_id: g
        for g in Grade.query.filter_by(lesson_id=lesson_id).all()
    }

    return render_template('teacher/grade_lesson.html',
        lesson=lesson,
        enrollments=enrollments,
        existing=existing,
    )
