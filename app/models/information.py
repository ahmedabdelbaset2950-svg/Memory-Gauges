from datetime import datetime
from app.extensions import db


class InformationMonth(db.Model):

    __tablename__ = "information_months"

    id = db.Column(db.Integer, primary_key=True)

    year = db.Column(
        db.Integer,
        nullable=False
    )

    month = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Open",
        nullable=False
    )

    closed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint(
            "year",
            "month",
            name="uq_information_month"
        ),
    )


class InformationRow(db.Model):

    __tablename__ = "information_rows"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================
    # Month / Group
    # =========================

    year = db.Column(
        db.Integer,
        nullable=False
    )

    month = db.Column(
        db.Integer,
        nullable=False
    )

    group_no = db.Column(
        db.Integer,
        nullable=False
    )

    # =========================
    # Job Information
    # =========================

    gauge_serial = db.Column(
        db.String(100)
    )

    from_date = db.Column(
        db.Date
    )

    to_date = db.Column(
        db.Date
    )

    days = db.Column(
        db.Float,
        default=0
    )

    well_number = db.Column(
        db.String(100)
    )

    changed_to = db.Column(
        db.String(100)
    )

    survey = db.Column(
        db.String(100)
    )

    type = db.Column(
        db.String(100)
    )

    rig_name = db.Column(
        db.String(100)
    )
    position = db.Column(db.String(20))

    bundle_carrier_sn = db.Column(
        db.String(100)
    )

    battery_sn = db.Column(
        db.String(100)
    )

    engineer = db.Column(
        db.String(100)
    )

    total_hours = db.Column(
        db.Float,
        default=0
    )

    total_samples = db.Column(
        db.Integer,
        default=0
    )

    comment = db.Column(
        db.Text
    )

    # =========================
    # Attachment
    # =========================

    attachment_filename = db.Column(
        db.String(255)
    )

    attachment_original_name = db.Column(
        db.String(255)
    )

    # =========================
    # Created
    # =========================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )