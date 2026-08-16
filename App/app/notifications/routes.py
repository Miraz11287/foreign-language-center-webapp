from flask import render_template, redirect, url_for, request, abort, jsonify, session
from flask_login import login_required, current_user
from app.notifications import notifications_bp
from app.extensions import db
from app.models.notification import Notification


@notifications_bp.route('/')
@login_required
def index():
    notes = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    # mark all as read when page is opened
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', notifications=notes)


@notifications_bp.route('/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_read(notif_id):
    n = db.session.get(Notification, notif_id) or abort(404)
    if n.user_id != current_user.id:
        abort(403)
    n.is_read = True
    db.session.commit()
    return redirect(n.link or url_for('notifications.index'))


@notifications_bp.route('/api/poll')
@login_required
def poll():
    """Return new unread notifications since last poll (for toast popups)."""
    last_id = session.get('last_notif_id', 0)
    new_notes = (
        Notification.query
        .filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
            Notification.id > last_id,
        )
        .order_by(Notification.id.asc())
        .all()
    )
    if new_notes:
        session['last_notif_id'] = new_notes[-1].id

    unread_total = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()

    return jsonify({
        'unread': unread_total,
        'new': [{'id': n.id, 'message': n.message, 'link': n.link} for n in new_notes],
    })
