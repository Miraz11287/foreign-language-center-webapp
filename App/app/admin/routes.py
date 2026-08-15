from flask import render_template
from flask_login import login_required
from app.admin import admin_bp
from app.auth.decorators import admin_required


@admin_bp.route('/')
@login_required
@admin_required
def index():
    # Часть 3: панель администратора
    return render_template('admin/index.html')
