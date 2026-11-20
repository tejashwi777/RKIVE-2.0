
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import Optional

from app.extensions import db
from app.models import TestExecution, TestRun, TestCase


test_executions = Blueprint(
    "test_executions",
    __name__,
    url_prefix="/test-executions"
)


class TestExecutionForm(FlaskForm):
    status = SelectField(
        "Execution Status",
        choices=[
            ("Not Run", "Not Run"),
            ("Pass", "Pass"),
            ("Fail", "Fail"),
            ("Blocked", "Blocked")
        ]
    )

    actual_result = TextAreaField(
        "Actual Result",
        validators=[Optional()]
    )

    execution_notes = TextAreaField(
        "Execution Notes",
        validators=[Optional()]
    )

    submit = SubmitField("Save Execution")


@test_executions.route("/run/<int:run_id>")
@login_required
def execution_list(run_id):
    run = db.get_or_404(TestRun, run_id)

    executions = TestExecution.query.filter_by(
        run_id=run.id
    ).all()

    return render_template(
        "test_executions/list.html",
        run=run,
        executions=executions
    )


@test_executions.route(
    "/<int:execution_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_execution(execution_id):
    execution = db.get_or_404(TestExecution, execution_id)

    form = TestExecutionForm(obj=execution)

    if form.validate_on_submit():
        form.populate_obj(execution)

        if form.status.data == "Not Run":
            execution.executed_by = None
            execution.executed_at = None
        else:
            execution.executed_by = current_user.id
            execution.executed_at = datetime.utcnow()

        update_run_status(execution.run_id)

    db.session.commit()

    flash("Test execution updated successfully.", "success")
    return redirect(
            url_for(
                "test_executions.execution_list",
                run_id=execution.run_id
            )
        )

    return render_template(
        "test_executions/edit.html",
        form=form,
        execution=execution
    )


@test_executions.route("/run/<int:run_id>/add-cases", methods=["POST"])
@login_required
def add_cases_to_run(run_id):
    run = db.get_or_404(TestRun, run_id)

    test_cases = TestCase.query.filter_by(
        suite_id=run.suite_id
    ).all()

    existing_case_ids = {
        execution.case_id
        for execution in TestExecution.query.filter_by(
            run_id=run.id
        ).all()
    }

    for case in test_cases:
        if case.id not in existing_case_ids:
            execution = TestExecution(
                run_id=run.id,
                case_id=case.id,
                status="Not Run"
            )
            db.session.add(execution)
    update_run_status(run.id)

    db.session.commit()

    flash("Test cases added to the execution run.", "success")

    return redirect(
        url_for(
            "test_executions.execution_list",
            run_id=run.id
        )
    )
def update_run_status(run_id):
    run = db.session.get(TestRun, run_id)

    executions = TestExecution.query.filter_by(
        run_id=run_id
    ).all()

    if not executions:
        run.status = "Not Started"

    elif all(
        execution.status != "Not Run"
        for execution in executions
    ):
        run.status = "Completed"

    elif any(
        execution.status != "Not Run"
        for execution in executions
    ):
        run.status = "In Progress"

    else:
        run.status = "Not Started"