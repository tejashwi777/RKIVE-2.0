
from datetime import datetime

from app.extensions import db


class TestExecution(db.Model):
    __tablename__ = "test_executions"

    id = db.Column(db.Integer, primary_key=True)

    run_id = db.Column(
        db.Integer,
        db.ForeignKey("test_runs.id"),
        nullable=False
    )

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("test_cases.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Not Run"
    )

    actual_result = db.Column(db.Text)
    execution_notes = db.Column(db.Text)

    executed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    executed_at = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    run = db.relationship("TestRun", backref="executions")
    test_case = db.relationship("TestCase", backref="executions")
    tester = db.relationship("User")

    def __repr__(self):
        return f"<TestExecution {self.id}: {self.status}>"
