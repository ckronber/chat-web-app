from numpy import broadcast
from .models import User
from .views import sio
from . import db
from flask import Blueprint,render_template,flash,redirect,request,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,logout_user,current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password,password):
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category = 'error')
        else:
            flash('Email does not exist',category='error')

    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup',methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        user_name = request.form.get('user_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        userEmail = User.query.filter_by(email=email).first()
        userName = User.query.filter_by(user_name=user_name).first()

        print(userName)
        if userEmail:
            flash('Email already exists',category='error')
        elif userName:
            flash('Username already exists',category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(user_name) < 2:
            flash('First Name must be greater than 1 characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
             #add user to database
             new_user = User(email = email, user_name = user_name, password = generate_password_hash(password1,method='sha256'))
             db.session.add(new_user)
             db.session.commit()
             login_user(new_user,remember=True)
             sio.emit("new_user",{"user_name":new_user.user_name,"id":new_user.id},broadcast=True)
             return redirect(url_for('views.home'))

    return render_template("sign_up.html",user=current_user)