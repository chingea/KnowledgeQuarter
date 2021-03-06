# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 19:24:27 2020

@author: Kirsch
"""

"""Routes for user authentication."""
from flask import Blueprint, redirect, render_template, flash, request, url_for
from flask_login import current_user, login_user
from forms import LoginForm, SignupForm
from model import db, User, Categories
from __init__ import login_manager


# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', "application",
    template_folder='templates',
    static_folder='static'
)


#Functionalities of the signup page
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():

    #Verify if the signup information are new and if so create a new entry in 
    #the SQLAlchemy databases of accounts and preferences
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            
            #Initiate a new user 
            user = User(
                name=form.name.data,
                email=form.email.data,
            )
            
            #Initiate a new preference row 
            prefs = Categories(
                email = form.email.data)
            
            
            #Update the users and preferences dataabses 
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.add(prefs)
            db.session.commit()
            ooo = Categories.query.first()
            print(ooo)
            ooo.time_in = False
            print(ooo)

            login_user(user)  # Log in as newly created user
            return redirect(url_for('main_bp.delivery_logger'))
        flash('A user already exists with that email address.')
    return render_template(
        'signup.html', form=form)


#Login logic
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    
    
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.delivery_logger'))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        #Check if user details are correct
        if user and user.check_password(password=form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main_bp.delivery_logger'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template(
        'login.html', form = form )
    



#Necessary login manager logics

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))