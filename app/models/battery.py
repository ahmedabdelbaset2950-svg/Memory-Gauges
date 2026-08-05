from datetime import datetime
from app.extensions import db


class Battery(db.Model):
    __tablename__ = "batteries"

    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(120), unique=True, nullable=False)
    compatible_gauge_type = db.Column(db.String(120), nullable=False)
    capacity = db.Column(db.Float, nullable=False)
    previous_consumption = db.Column(
    db.Float,
    nullable=False,
    default=0.0
)
    capacity_unit = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Available")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Battery {self.serial_number}>"
