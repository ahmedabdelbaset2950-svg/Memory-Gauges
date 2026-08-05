from datetime import datetime
from app.extensions import db


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    # تاريخ الجوب داخل الجدول
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)

    # بيانات البئر
    well_number = db.Column(db.String(100), nullable=False)

    # المعدة المستخدمة
    equipment_type = db.Column(db.String(20), nullable=False)   # gauge / bundle
    equipment_id = db.Column(db.Integer, nullable=False)

    # حالة الجوب
    status = db.Column(db.String(30), default="Open")

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Job {self.id} - {self.well_number}>"
class JobColumn(db.Model):

    __tablename__ = "job_columns"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    equipment_type = db.Column(db.String(20), nullable=False)

    month = db.Column(db.Integer, nullable=False)

    year = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )