
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, SubmitField
)
from wtforms.validators import DataRequired, Length

from app.extensions import db
from app.models import TestCase, TestSuite, Requirement


test_cases = Blueprint(
    "test_cases",
    __name__,
    url_prefix="/test-cases"
)


class TestCaseForm(FlaskForm):
    case_key = StringField(
        "Test Case ID",
        validators=[DataRequired(), Length(max=30)]
    )

    title = StringField(
        "Title",
        validators=[DataRequired(), Length(max=200)]
    )

    description = TextAreaField("Description")
    preconditions = TextAreaField("Preconditions")

    test_steps = TextAreaField(
        "Test Steps",
        validators=[DataRequired()]
    )

    expected_result = TextAreaField(
        "Expected Result",
        validators=[DataRequired()]
    )

    priority = SelectField(
        "Priority",
        choices=[
            ("Critical", "Critical"),
            ("High", "High"),
            ("Medium", "Medium"),
            ("Low", "Low")
        ]
    )

    status = SelectField(
        "Status",
        choices=[
            ("Draft", "Draft"),
            ("Ready", "Ready"),
            ("Retired", "Retired")
        ]
    )

    suite_id = SelectField(
        "Test Suite",
        coerce=int,
        validators=[DataRequired()]
    )

    requirement_id = SelectField(
        "Linked Requirement",
        coerce=int,
        choices=[(0, "No linked requirement")]
    )

    submit = SubmitField("Save Test Case")


def populate_choices(form):
    form.suite_id.choices = [
        (suite.id, f"{suite.suite_key} - {suite.name}")
        for suite in TestSuite.query.order_by(TestSuite.name).all()
    ]

    form.requirement_id.choices = [
        (0, "No linked requirement")
    ] + [
        (req.id, f"{req.requirement_key} - {req.title}")
        for req in Requirement.query.order_by(Requirement.title).all()
    ]


@test_cases.route("/")
@login_required
def case_list():
    cases = TestCase.query.order_by(
        TestCase.created_at.desc()
    ).all()

    return render_template(
        "test_cases/list.html",
        cases=cases
    )


@test_cases.route("/create", methods=["GET", "POST"])
@login_required
def create_case():
    form = TestCaseForm()
    populate_choices(form)

    if not form.suite_id.choices:
        flash("Create a test suite before adding test cases.", "warning")
        return redirect(url_for("test_suites.suite_list"))

    if form.validate_on_submit():
        key = form.case_key.data.strip().upper()

        existing = TestCase.query.filter_by(
            case_key=key
        ).first()

        if existing:
            flash("This test case ID already exists.", "danger")
        else:
            case = TestCase(
                case_key=key,
                title=form.title.data.strip(),
                description=(form.description.data or "").strip(),
                preconditions=(form.preconditions.data or "").strip(),
                test_steps=form.test_steps.data.strip(),
                expected_result=form.expected_result.data.strip(),
                priority=form.priority.data,
                status=form.status.data,
                suite_id=form.suite_id.data,
                requirement_id=form.requirement_id.data or None,
                created_by=current_user.id
            )

            db.session.add(case)
            db.session.commit()

            flash("Test case created successfully!", "success")
            return redirect(url_for("test_cases.case_list"))

    return render_template(
        "test_cases/create.html",
        form=form
    )


@test_cases.route("/<int:case_id>/edit", methods=["GET", "POST"])
@login_required
def edit_case(case_id):
    case = db.get_or_404(TestCase, case_id)

    form = TestCaseForm(obj=case)
    populate_choices(form)

    if form.validate_on_submit():
        key = form.case_key.data.strip().upper()

        duplicate = TestCase.query.filter(
            TestCase.case_key == key,
            TestCase.id != case.id
        ).first()

        if duplicate:
            flash("This test case ID already exists.", "danger")
        else:
            case.case_key = key
            case.title = form.title.data.strip()
            case.description = (form.description.data or "").strip()
            case.preconditions = (form.preconditions.data or "").strip()
            case.test_steps = form.test_steps.data.strip()
            case.expected_result = form.expected_result.data.strip()
            case.priority = form.priority.data
            case.status = form.status.data
            case.suite_id = form.suite_id.data
            case.requirement_id = form.requirement_id.data or None

            db.session.commit()

            flash("Test case updated successfully!", "success")
            return redirect(url_for("test_cases.case_list"))

    return render_template(
        "test_cases/edit.html",
        form=form,
        case=case
    )


@test_cases.route("/<int:case_id>/delete", methods=["POST"])
@login_required
def delete_case(case_id):
    case = db.get_or_404(TestCase, case_id)

    db.session.delete(case)
    db.session.commit()

    flash("Test case deleted successfully!", "success")
    return redirect(url_for("test_cases.case_list"))
