
from datetime import datetime

from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(120),
        nullable=False
    )

    project_key = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    description = db.Column(db.Text)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Planning"
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    owner = db.relationship(
        "User",
        backref="projects"
    )

    def __repr__(self):
        return f"<Project {self.project_key}>"
