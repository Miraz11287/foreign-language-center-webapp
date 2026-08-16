from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm
from app.extensions import db
from app.models.user import User, Role


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=form.email.data.lower().strip(),
            role=Role.student,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid email or password.', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from app.auth.profile_forms import EditProfileForm, ChangePasswordForm

    profile_form  = EditProfileForm(obj=current_user, prefix='profile')
    password_form = ChangePasswordForm(prefix='password')

    if profile_form.submit.data and profile_form.validate():
        current_user.first_name = profile_form.first_name.data.strip()
        current_user.last_name  = profile_form.last_name.data.strip()
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('auth.profile'))

    if password_form.submit.data and password_form.validate():
        if not current_user.check_password(password_form.current.data):
            flash('Current password is incorrect.', 'error')
        else:
            current_user.set_password(password_form.new_pass.data)
            db.session.commit()
            flash('Password changed.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html',
        profile_form=profile_form,
        password_form=password_form,
    )
