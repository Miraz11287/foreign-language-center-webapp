from flask import render_template, redirect, url_for, request, abort
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
