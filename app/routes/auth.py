
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

auth = Blueprint("auth", __name__)


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(), Length(min=3, max=80)
    ])
    email = StringField("Email", validators=[
        DataRequired(), Email(), Length(max=120)
    ])
    password = PasswordField("Password", validators=[
        DataRequired(), Length(min=8)
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(), EqualTo("password")
    ])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(), Email()
    ])
    password = PasswordField("Password", validators=[
        DataRequired()
    ])
    submit = SubmitField("Login")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data.lower())
        ).first()

        if existing_user:
            flash("Username or email already exists.", "danger")
            return render_template("register.html", form=form)

        user = User(
            username=form.username.data.strip(),
            email=form.email.data.lower(),
            role="QA Tester"
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data.lower()
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(url_for("main.home"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
