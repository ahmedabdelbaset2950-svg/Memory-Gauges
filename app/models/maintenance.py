from datetime import datetime
from app.extensions import db


class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_records"

    id = db.Column(db.Integer, primary_key=True)
    equipment_type = db.Column(db.String(30), nullable=False)
    serial_number = db.Column(db.String(120), nullable=False, index=True)
    maintenance_date = db.Column(db.Date, nullable=False)
    problem = db.Column(db.Text, nullable=False)
    action_taken = db.Column(db.Text)
    status = db.Column(db.String(30), nullable=False, default="Maintenance")
    return_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
