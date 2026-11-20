
from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, abort
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from app.extensions import db
from app.models import Project


projects = Blueprint("projects", __name__, url_prefix="/projects")


class ProjectForm(FlaskForm):
    name = StringField(
        "Project Name",
        validators=[DataRequired(), Length(max=120)]
    )

    project_key = StringField(
        "Project Key",
        validators=[DataRequired(), Length(min=2, max=20)]
    )

    description = TextAreaField("Description")

    status = SelectField(
        "Project Status",
        choices=[
            ("Planning", "Planning"),
            ("Active", "Active"),
            ("On Hold", "On Hold"),
            ("Completed", "Completed")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Save Project")


def can_manage(project):
    return (
        current_user.role == "Admin"
        or (
            current_user.role == "QA Tester"
            and project.created_by == current_user.id
        )
    )


@projects.route("/")
@login_required
def project_list():
    all_projects = Project.query.order_by(
        Project.created_at.desc()
    ).all()

    return render_template(
        "projects/list.html",
        projects=all_projects
    )


@projects.route("/create", methods=["GET", "POST"])
@login_required
def create_project():
    if current_user.role not in ["Admin", "QA Tester"]:
        abort(403)

    form = ProjectForm()

    if form.validate_on_submit():
        project_key = form.project_key.data.strip().upper()

        existing = Project.query.filter_by(
            project_key=project_key
        ).first()

        if existing:
            flash("That project key is already in use.", "danger")
            return render_template("projects/create.html", form=form)

        project = Project(
            name=form.name.data.strip(),
            project_key=project_key,
            description=(form.description.data or "").strip(),
            status=form.status.data,
            created_by=current_user.id
        )

        db.session.add(project)
        db.session.commit()

        flash("Project created successfully!", "success")
        return redirect(url_for("projects.project_list"))

    return render_template("projects/create.html", form=form)


@projects.route("/<int:project_id>")
@login_required
def project_detail(project_id):
    project = db.get_or_404(Project, project_id)

    return render_template(
        "projects/detail.html",
        project=project
    )


@projects.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    project = db.get_or_404(Project, project_id)

    if not can_manage(project):
        abort(403)

    form = ProjectForm(obj=project)

    if form.validate_on_submit():
        project_key = form.project_key.data.strip().upper()

        duplicate = Project.query.filter(
            Project.project_key == project_key,
            Project.id != project.id
        ).first()

        if duplicate:
            flash("That project key is already in use.", "danger")
            return render_template(
                "projects/edit.html",
                form=form,
                project=project
            )

        project.name = form.name.data.strip()
        project.project_key = project_key
        project.description = (form.description.data or "").strip()
        project.status = form.status.data

        db.session.commit()

        flash("Project updated successfully!", "success")
        return redirect(
            url_for("projects.project_detail", project_id=project.id)
        )

    return render_template(
        "projects/edit.html",
        form=form,
        project=project
    )
