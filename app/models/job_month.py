from datetime import datetime

from app.extensions import db


class JobMonth(db.Model):

    __tablename__ = "job_months"

    id = db.Column(db.Integer, primary_key=True)

    year = db.Column(db.Integer, nullable=False)

    month = db.Column(db.Integer, nullable=False)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Open"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    closed_at = db.Column(
        db.DateTime,
        nullable=True
    )