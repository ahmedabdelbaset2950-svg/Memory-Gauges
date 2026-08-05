from datetime import datetime

from app.extensions import db


class AppSettings(db.Model):
    __tablename__ = "app_settings"

    id = db.Column(db.Integer, primary_key=True)

    # ==========================
    # Company
    # ==========================

    company_name = db.Column(
        db.String(150),
        default="MGMS"
    )

    company_logo = db.Column(
        db.String(255),
        default="default_logo.png"
    )

    company_email = db.Column(
        db.String(120)
    )

    company_phone = db.Column(
        db.String(50)
    )

    company_address = db.Column(
        db.String(255)
    )

    # ==========================
    # System
    # ==========================

    

    timezone = db.Column(
        db.String(50),
        default="Africa/Cairo"
    )

    date_format = db.Column(
        db.String(30),
        default="%d %b %Y"
    )

    time_format = db.Column(
        db.String(20),
        default="%H:%M:%S"
    )

    theme = db.Column(
        db.String(20),
        default="Light"
    )

    # ==========================
    # Info
    # ==========================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )