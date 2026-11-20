
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from app.extensions import db
from app.models import Requirement, Project

requirements = Blueprint(
    "requirements",
    __name__,
    url_prefix="/requirements"
)


class RequirementForm(FlaskForm):
    requirement_key = StringField(
        "Requirement ID",
        validators=[DataRequired(), Length(max=30)]
    )

    title = StringField(
        "Requirement Title",
        validators=[DataRequired(), Length(max=200)]
    )

    description = TextAreaField("Description")

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
            ("Approved", "Approved"),
            ("Implemented", "Implemented"),
            ("Rejected", "Rejected")
        ]
    )

    project_id = SelectField(
        "Project",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Requirement")


@requirements.route("/")
@login_required
def requirement_list():
    all_requirements = Requirement.query.order_by(
        Requirement.created_at.desc()
    ).all()

    return render_template(
        "requirements/list.html",
        requirements=all_requirements
    )


@requirements.route("/create", methods=["GET", "POST"])
@login_required
def create_requirement():
    form = RequirementForm()

    form.project_id.choices = [
        (project.id, project.name)
        for project in Project.query.order_by(Project.name).all()
    ]

    if not form.project_id.choices:
        flash("Create a project before adding requirements.", "warning")
        return redirect(url_for("projects.project_list"))

    if form.validate_on_submit():
        key = form.requirement_key.data.strip().upper()

        existing = Requirement.query.filter_by(
            requirement_key=key
        ).first()

        if existing:
            flash("This requirement ID already exists.", "danger")
        else:
            requirement = Requirement(
                requirement_key=key,
                title=form.title.data.strip(),
                description=(form.description.data or "").strip(),
                priority=form.priority.data,
                status=form.status.data,
                project_id=form.project_id.data,
                created_by=current_user.id
            )

            db.session.add(requirement)
            db.session.commit()

            flash("Requirement created successfully!", "success")
            return redirect(url_for("requirements.requirement_list"))

    return render_template(
        "requirements/create.html",
        form=form
    )


@requirements.route("/<int:requirement_id>/edit", methods=["GET", "POST"])
@login_required
def edit_requirement(requirement_id):
    requirement = db.get_or_404(Requirement, requirement_id)

    form = RequirementForm(obj=requirement)

    form.project_id.choices = [
        (project.id, project.name)
        for project in Project.query.order_by(Project.name).all()
    ]

    if form.validate_on_submit():
        key = form.requirement_key.data.strip().upper()

        duplicate = Requirement.query.filter(
            Requirement.requirement_key == key,
            Requirement.id != requirement.id
        ).first()

        if duplicate:
            flash("This requirement ID already exists.", "danger")
        else:
            requirement.requirement_key = key
            requirement.title = form.title.data.strip()
            requirement.description = (form.description.data or "").strip()
            requirement.priority = form.priority.data
            requirement.status = form.status.data
            requirement.project_id = form.project_id.data

            db.session.commit()

            flash("Requirement updated successfully!", "success")
            return redirect(url_for("requirements.requirement_list"))

    return render_template(
        "requirements/edit.html",
        form=form,
        requirement=requirement
    )


@requirements.route("/<int:requirement_id>/delete", methods=["POST"])
@login_required
def delete_requirement(requirement_id):
    requirement = db.get_or_404(Requirement, requirement_id)

    db.session.delete(requirement)
    db.session.commit()

    flash("Requirement deleted successfully!", "success")
    return redirect(url_for("requirements.requirement_list"))
