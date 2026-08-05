from datetime import datetime

from app.extensions import db


class MemoryGauge(db.Model):

    __tablename__ = "memory_gauges"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    serial_number = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    company = db.Column(
        db.String(100),
        nullable=False
    )

    gauge_type = db.Column(
        db.String(100),
        nullable=False
    )

    # ======================================
    # Bundle Compatibility
    # ======================================

    supports_dual = db.Column(
        db.Boolean,
        default=False
    )

    dual_type = db.Column(
        db.String(20),
        default="Both"
    )

    supports_quad = db.Column(
        db.Boolean,
        default=False
    )

    quad_type = db.Column(
        db.String(20),
        default="Both"
    )

    calibration_date = db.Column(
        db.Date,
        nullable=True
    )

    battery_serial = db.Column(
        db.String(100)
    )

    status = db.Column(
        db.String(50),
        default="Available"
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):

        return f"<MemoryGauge {self.serial_number}>"
