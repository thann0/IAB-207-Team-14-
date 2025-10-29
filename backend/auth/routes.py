#import all the necessary moduls
from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from ..extensions import db
from ..models import User
from ..forms import RegisterForm, LoginForm



# create the blueprint for authentication
auth_bp = Blueprint("auth", __name__)

#the register route hadles POST and GET requests
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    
    #debug show validation errors on every post in the terminal- shows form data and errors in the terminal
    if request.method == "POST":
        print("DEBUG form.data (no passwords):", {k:v for k,v in form.data.items() if k not in ["password", "confirm"]})
        print ("DEBUG form.errors:", form.errors)
        
    #when the form is valid and submitted...
    if form.validate_on_submit():
        #now check for the existing emailxf
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash("This email is already registered.", "danger")
            return render_template("auth/register.html", form=form)
        
        #check for the existing username
        if User.query.filter_by(username=form.user_name.data.strip()).first():
            flash("This username is taken", "danger")
            return render_template("auth/register.html", form=form)
        #create a new user from the form and save the details to the db 
        user = User.create_from_form(form)         
        db.session.add(user)
        db.session.commit()
        
        #redirect to login and success flash alert
        flash("Registration successful! You can now finally login.", "success")
        return redirect(url_for("auth.login"))
    
    #if GET or the validation fails
    return render_template("auth/register.html", form=form)

#simple login with login logic
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.user_name.data.strip()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("You have logged in successfully", "success")
            
            next_url = request.args.get("next")
            return redirect(next_url or url_for("events.event_detail", event_id=1))
        
        flash("Invalid password or email.", "danger")
    return render_template("auth/login.html", form=form)

#logout route
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out,", "info")
    return redirect(url_for("auth.loginn"))
        
        