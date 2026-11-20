
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from app.extensions import db
from app.models import TestRun, TestSuite


test_runs = Blueprint(
    "test_runs",
    __name__,
    url_prefix="/test-runs"
)


class TestRunForm(FlaskForm):
    run_key = StringField(
        "Run Key",
        validators=[DataRequired(), Length(max=30)]
    )

    name = StringField(
        "Run Name",
        validators=[DataRequired(), Length(max=150)]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    suite_id = SelectField(
        "Test Suite",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Test Run")


def populate_choices(form):
    suites = TestSuite.query.order_by(TestSuite.name).all()

    form.suite_id.choices = [
        (suite.id, f"{suite.suite_key} - {suite.name}")
        for suite in suites
    ]


@test_runs.route("/")
@login_required
def run_list():
    runs = TestRun.query.order_by(TestRun.created_at.desc()).all()

    return render_template(
        "test_runs/list.html",
        runs=runs
    )


@test_runs.route("/create", methods=["GET", "POST"])
@login_required
def create_run():
    form = TestRunForm()

    populate_choices(form)

    if not form.suite_id.choices:
        flash("Create a test suite before creating a test run.", "warning")
        return redirect(url_for("test_suites.suite_list"))

    if form.validate_on_submit():
        existing_run = TestRun.query.filter_by(
            run_key=form.run_key.data.strip()
        ).first()

        if existing_run:
            flash("This Test Run Key already exists.", "danger")
            return render_template("test_runs/create.html", form=form)

        run = TestRun(
            run_key=form.run_key.data.strip(),
            name=form.name.data.strip(),
            description=form.description.data,
            suite_id=form.suite_id.data,
            created_by=current_user.id
        )

        db.session.add(run)
        db.session.commit()

        flash("Test Run created successfully.", "success")

        return redirect(url_for("test_runs.run_list"))

    return render_template(
        "test_runs/create.html",
        form=form
    )


@test_runs.route("/<int:run_id>")
@login_required
def run_detail(run_id):
    run = db.get_or_404(TestRun, run_id)

    return render_template(
        "test_runs/detail.html",
        run=run
    )
