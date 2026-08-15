import click
from flask import current_app
from app.extensions import db
from app.models.user import User, Role


def register_commands(app):
    @app.cli.command('seed')
    def seed():
        """Создать начального администратора."""
        if User.query.filter_by(email='admin@langcenter.ru').first():
            click.echo('Администратор уже существует.')
            return
        admin = User(
            first_name='Admin',
            last_name='LangCenter',
            email='admin@langcenter.ru',
            role=Role.admin,
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        click.echo('Создан администратор: admin@langcenter.ru / admin123')
