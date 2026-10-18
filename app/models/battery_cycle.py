
from datetime import date

from app.extensions import db


class BatteryCycle(db.Model):
    __tablename__ = "battery_cycles"

    id = db.Column(db.Integer, primary_key=True)

    battery_id = db.Column(
        db.Integer,
        db.ForeignKey("batteries.id"),
        nullable=False,
        index=True
    )

    cycle_number = db.Column(
        db.Integer,
        nullable=False
    )

    started_on = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    # آخر يوم في الدورة القديمة.
    # None يعني أن هذه هي الدورة الحالية.
    ended_on = db.Column(
        db.Date,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    battery = db.relationship(
        "Battery",
        backref=db.backref(
            "cycles",
            lazy="dynamic",
            cascade="all, delete-orphan"
        )
    )

    __table_args__ = (
        db.UniqueConstraint(
            "battery_id",
            "cycle_number",
            name="uq_battery_cycle_number"
        ),
    )
