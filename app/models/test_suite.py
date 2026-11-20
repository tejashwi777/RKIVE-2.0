
from datetime import datetime

from app.extensions import db


class TestSuite(db.Model):
    __tablename__ = "test_suites"

    id = db.Column(db.Integer, primary_key=True)

    suite_key = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
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

    project = db.relationship(
        "Project",
        backref="test_suites"
    )

    creator = db.relationship("User")

    def __repr__(self):
        return f"<TestSuite {self.suite_key}>"
