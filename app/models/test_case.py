
from datetime import datetime

from app.extensions import db


class TestCase(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.Integer, primary_key=True)

    case_key = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    preconditions = db.Column(db.Text)
    test_steps = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Medium"
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Draft"
    )

    suite_id = db.Column(
        db.Integer,
        db.ForeignKey("test_suites.id"),
        nullable=False
    )

    requirement_id = db.Column(
        db.Integer,
        db.ForeignKey("requirements.id"),
        nullable=True
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

    suite = db.relationship(
        "TestSuite",
        backref="test_cases"
    )

    requirement = db.relationship(
        "Requirement",
        backref="test_cases"
    )

    creator = db.relationship("User")

    def __repr__(self):
        return f"<TestCase {self.case_key}>"
