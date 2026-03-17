from flask import Blueprint, render_template, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from .models import User  # assuming models is in same package or imported via `from ..models`
from . import db
from .extensions import sio

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            
            # 🔹 Update DB: mark as online (HTTP-level status update)
            user.user_online = True
            db.session.commit()
            
            # 🔹 Notify all connected clients about new online user
            sio.emit(
                'user_status',
                {'id': user.id, 'status': True},
                broadcast=True
            )
            
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.home'))

        else:
            flash('Invalid email or password.', category='error')

    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    # 🔹 Mark as offline BEFORE logging out
    current_user.user_online = False
    db.session.commit()

    sio.emit(
        'user_status',
        {'id': current_user.id, 'status': False},
        broadcast=True
    )

    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('user_name')  # NOTE: 'user_name' → 'username'? be consistent
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user_by_email = User.query.filter_by(email=email).first()
        user_by_username = User.query.filter_by(user_name=username).first()

        if user_by_email:
            flash('Email already registered.', category='error')
        elif user_by_username:
            flash('Username already taken.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif len(username) < 2:
            flash('Username must be at least 2 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(
                email=email,
                user_name=username,
                password=generate_password_hash(password1, method='sha256'),
                user_online=False  # will be set to True on login
            )
            db.session.add(new_user)
            db.session.commit()

            flash('Account created! You can now log in.', category='success')
            return redirect(url_for('auth.login'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except Exception:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first_or_404()

    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.email_confirmed = True
        user.confirmed_at = datetime.utcnow()
        db.session.commit()
        flash('Your email has been confirmed! You can now log in.', 'success')

    return redirect(url_for('auth.login'))