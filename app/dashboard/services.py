import calendar
from datetime import date

from sqlalchemy import func

from app.extensions import db
from app.models.memory_gauge import MemoryGauge
from app.models.bundle_carrier import BundleCarrier
from app.models.battery import Battery
from app.models.jobs import Job
from app.models.information import InformationRow

def get_equipment_counts():
    """
    ترجع عدد كل نوع من المعدات المسجلة.
    """

    total_gauges = db.session.query(func.count(MemoryGauge.id)).scalar() or 0
    total_band = db.session.query(func.count(BundleCarrier.id)).scalar() or 0
    total_batteries = db.session.query(func.count(Battery.id)).scalar() or 0

    return {
        "total_gauges": total_gauges,
        "total_band": total_band,
        "total_batteries": total_batteries,
        "total_equipment": total_gauges + total_band,
    }


def get_job_counts(year, month):
    """
    عدد الجوبز في السنة الحالية، وعدد الجوبز في الشهر الحالي.
    """

    annual_jobs = (
        db.session.query(func.count(Job.id))
        .filter(Job.year == year)
        .scalar()
        or 0
    )

    monthly_jobs = (
        db.session.query(func.count(Job.id))
        .filter(Job.year == year, Job.month == month)
        .scalar()
        or 0
    )

    return annual_jobs, monthly_jobs


def get_gauge_used_year(year):

    rows = (
        db.session.query(
            InformationRow.gauge_serial,
            func.count(InformationRow.id),
        )
        .filter(
            InformationRow.year == year,
            InformationRow.gauge_serial.isnot(None),
            InformationRow.gauge_serial != "",
        )
        .group_by(InformationRow.gauge_serial)
        .order_by(func.count(InformationRow.id).desc())
        .all()
    )

    return [[r[0], r[1]] for r in rows]


def get_gauge_used_month(year, month):

    rows = (
        db.session.query(
            InformationRow.gauge_serial,
            func.count(InformationRow.id),
        )
        .filter(
            InformationRow.year == year,
            InformationRow.month == month,
            InformationRow.gauge_serial.isnot(None),
            InformationRow.gauge_serial != "",
        )
        .group_by(InformationRow.gauge_serial)
        .order_by(func.count(InformationRow.id).desc())
        .all()
    )

    return [[r[0], r[1]] for r in rows]


def get_changed_gauge_year(year):

    rows = (
        db.session.query(
            InformationRow.changed_to,
            func.count(InformationRow.id),
        )
        .filter(
            InformationRow.year == year,
            InformationRow.changed_to.isnot(None),
            InformationRow.changed_to != "",
        )
        .group_by(InformationRow.changed_to)
        .order_by(func.count(InformationRow.id).desc())
        .all()
    )

    return [[r[0], r[1]] for r in rows]


def get_changed_gauge_month(year, month):

    rows = (
        db.session.query(
            InformationRow.changed_to,
            func.count(InformationRow.id),
        )
        .filter(
            InformationRow.year == year,
            InformationRow.month == month,
            InformationRow.changed_to.isnot(None),
            InformationRow.changed_to != "",
        )
        .group_by(InformationRow.changed_to)
        .order_by(func.count(InformationRow.id).desc())
        .all()
    )

    return [[r[0], r[1]] for r in rows]

def get_upcoming_calibrations(limit=5):
    """
    أقرب الجوجات لتاريخ المعايرة المسجل (calibration_date)، الأقرب أولاً.
    ملاحظة: calibration_date هنا بيمثل تاريخ آخر/المقرر معايرة كما هو مسجل بالنظام،
    فمفيش دورية معايرة منفصلة محسوبة حاليًا.
    """

    today = date.today()

    gauges = (
        MemoryGauge.query.filter(MemoryGauge.calibration_date.isnot(None))
        .order_by(MemoryGauge.calibration_date.asc())
        .limit(limit)
        .all()
    )

    result = []

    for g in gauges:
        days_left = (g.calibration_date - today).days

        result.append({
            "serial": g.serial_number,
            "type": "Memory Gauge",
            "due_date": g.calibration_date,
            "days_left": days_left,
        })

    return result
