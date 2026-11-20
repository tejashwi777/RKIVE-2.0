from datetime import datetime

from app.extensions import db


class TestRun(db.Model):
    __tablename__ = "test_runs"

    id = db.Column(db.Integer, primary_key=True)

    run_key = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    suite_id = db.Column(
        db.Integer,
        db.ForeignKey("test_suites.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Not Started"
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

    suite = db.relationship("TestSuite", backref="test_runs")
    creator = db.relationship("User")

    def __repr__(self):
        return f"<TestRun {self.run_key}>"