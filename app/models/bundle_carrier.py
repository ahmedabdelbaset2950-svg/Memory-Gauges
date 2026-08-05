from datetime import datetime

from app.extensions import db


class BundleCarrier(db.Model):

    __tablename__ = "bundle_carriers"

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
        db.String(120),
        nullable=False
    )

    type = db.Column(
        db.String(50),
        nullable=False
    )

    position = db.Column(
        db.String(20),
        nullable=False
    )
    pressure_test_date = db.Column(db.Date, nullable=True)

    current_location = db.Column(
        db.String(150)
    )

    allen_key = db.Column(
        db.String(120)
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):

        return f"<BundleCarrier {self.serial_number}>"