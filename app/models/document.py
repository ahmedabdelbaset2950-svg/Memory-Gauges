from datetime import datetime

from app.extensions import db


CATEGORY_CHOICES = [
    ("calibration_certificate", "Calibration Certificate"),
    ("pressure_test", "Pressure Test Report"),
    ("risk_assessment", "Risk Assessment"),
    ("work_procedure", "Work Procedure"),
    ("gauge_photo", "Gauge Photo"),
    ("other", "Other"),
]


class Document(db.Model):

    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    category = db.Column(db.String(50), nullable=False, default="other")

    # ربط اختياري بمعدة (جيدج أو باندل كاريير بس)
    equipment_type = db.Column(db.String(20))   # "gauge" أو "bundle"
    equipment_id = db.Column(db.Integer)

    file_filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_ext = db.Column(db.String(10))

    expiry_date = db.Column(db.Date)

    notes = db.Column(db.Text)

    uploaded_by = db.Column(db.String(120))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Document {self.title}>"
