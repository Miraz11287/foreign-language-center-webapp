from flask import render_template
from app.main import main_bp


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/schedule')
def schedule():
    # Часть 4: расписание
    return render_template('schedule.html')
