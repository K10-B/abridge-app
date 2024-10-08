from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import os
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password_hash is None:
                flash("This account needs to reset the password, please contact support.", category='error')
            elif user.check_password(password):
                flash("Logged in successfully!", category='success')
                login_user(user, remember=remember)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect email or password, try again.", category='error')
        else:
            flash("User not found.", category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            try:
                new_user = User(email=email, first_name=first_name)
                new_user.set_password(password1)  # Use the set_password method
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash("Account created!", category='success')
                return redirect(url_for('views.home'))
            except IntegrityError:
                db.session.rollback()
                flash('An unexpected error occurred. Please try again.', category='error')
    
    return render_template("sign_up.html", user=current_user)