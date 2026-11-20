
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from app.extensions import db
from app.models import TestSuite, Project


test_suites = Blueprint(
    "test_suites",
    __name__,
    url_prefix="/test-suites"
)


class TestSuiteForm(FlaskForm):
    suite_key = StringField(
        "Suite ID",
        validators=[DataRequired(), Length(max=30)]
    )

    name = StringField(
        "Suite Name",
        validators=[DataRequired(), Length(max=150)]
    )

    description = TextAreaField("Description")

    project_id = SelectField(
        "Project",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Test Suite")


@test_suites.route("/")
@login_required
def suite_list():
    suites = TestSuite.query.order_by(
        TestSuite.created_at.desc()
    ).all()

    return render_template(
        "test_suites/list.html",
        suites=suites
    )


@test_suites.route("/create", methods=["GET", "POST"])
@login_required
def create_suite():
    form = TestSuiteForm()

    form.project_id.choices = [
        (project.id, project.name)
        for project in Project.query.order_by(Project.name).all()
    ]

    if not form.project_id.choices:
        flash("Create a project before adding test suites.", "warning")
        return redirect(url_for("projects.project_list"))

    if form.validate_on_submit():
        key = form.suite_key.data.strip().upper()

        existing = TestSuite.query.filter_by(
            suite_key=key
        ).first()

        if existing:
            flash("This suite ID already exists.", "danger")
        else:
            suite = TestSuite(
                suite_key=key,
                name=form.name.data.strip(),
                description=(form.description.data or "").strip(),
                project_id=form.project_id.data,
                created_by=current_user.id
            )

            db.session.add(suite)
            db.session.commit()

            flash("Test suite created successfully!", "success")

            return redirect(url_for("test_suites.suite_list"))

    return render_template(
        "test_suites/create.html",
        form=form
    )


@test_suites.route("/<int:suite_id>/edit", methods=["GET", "POST"])
@login_required
def edit_suite(suite_id):
    suite = db.get_or_404(TestSuite, suite_id)

    form = TestSuiteForm(obj=suite)

    form.project_id.choices = [
        (project.id, project.name)
        for project in Project.query.order_by(Project.name).all()
    ]

    if form.validate_on_submit():
        key = form.suite_key.data.strip().upper()

        duplicate = TestSuite.query.filter(
            TestSuite.suite_key == key,
            TestSuite.id != suite.id
        ).first()

        if duplicate:
            flash("This suite ID already exists.", "danger")
        else:
            suite.suite_key = key
            suite.name = form.name.data.strip()
            suite.description = (form.description.data or "").strip()
            suite.project_id = form.project_id.data

            db.session.commit()

            flash("Test suite updated successfully!", "success")

            return redirect(url_for("test_suites.suite_list"))

    return render_template(
        "test_suites/edit.html",
        form=form,
        suite=suite
    )


@test_suites.route("/<int:suite_id>/delete", methods=["POST"])
@login_required
def delete_suite(suite_id):
    suite = db.get_or_404(TestSuite, suite_id)

    db.session.delete(suite)
    db.session.commit()

    flash("Test suite deleted successfully!", "success")

    return redirect(url_for("test_suites.suite_list"))
