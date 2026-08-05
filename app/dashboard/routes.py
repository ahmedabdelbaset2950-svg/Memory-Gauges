from datetime import date

from flask import render_template
from flask_login import login_required
from sqlalchemy import distinct

from app.extensions import db
from app.dashboard import dashboard_bp
from app.dashboard.services import (
     get_equipment_counts,
    get_gauge_used_year,
    get_gauge_used_month,
    get_changed_gauge_year,
    get_changed_gauge_month,
    get_upcoming_calibrations,
)

from app.models.information import InformationRow
from flask import request
import calendar


class month_names:
    """Utility class providing month name helpers for templates."""

    def get_all(self):
        """Return full month names as a list indexed 1-12 (0 unused)."""
        # calendar.month_name is 0-indexed with an empty string at 0
        return list(calendar.month_name)

    def get_name(self, month: int) -> str:
        """Return full month name for given 1-12 integer, empty string otherwise."""
        if 1 <= month <= 12:
            return calendar.month_name[month]
        return ""

    def get_abbr(self, month: int) -> str:
        """Return abbreviated month name for given 1-12 integer, empty string otherwise."""
        if 1 <= month <= 12:
            return calendar.month_abbr[month]
        return ""

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    today = date.today()

    selected_year = request.args.get(
    "year",
    default=today.year,
    type=int,
)

    selected_month = request.args.get(
    "month",
    default=today.month,
    type=int,
)

    equipment_counts = get_equipment_counts()

    # ==========================================
    # Jobs Statistics (From Information Module)
    # ==========================================

    annual_jobs = (
    db.session.query(
        InformationRow.year,
        InformationRow.month,
        InformationRow.group_no,
    )
    .filter(InformationRow.year == selected_year)
    .distinct()
    .count()
)

    monthly_jobs = (
    db.session.query(
        InformationRow.month,
        InformationRow.group_no,
    )
    .filter(
        InformationRow.year == selected_year,
        InformationRow.month == selected_month,
    )
    .distinct()
    .count()
)

    gauge_used_year = get_gauge_used_year(selected_year)

    gauge_used_month = get_gauge_used_month(
    selected_year,
    selected_month,
)

    changed_gauge_year = get_changed_gauge_year(selected_year)

    changed_gauge_month = get_changed_gauge_month(
    selected_year,
    selected_month,
)

    upcoming_calibrations = get_upcoming_calibrations(limit=5)

    return render_template(

        "dashboard/dashboard.html",

        total_equipment=equipment_counts["total_equipment"],
        total_gauges=equipment_counts["total_gauges"],
        total_band=equipment_counts["total_band"],
        total_batteries=equipment_counts["total_batteries"],

        annual_jobs=annual_jobs,
        monthly_jobs=monthly_jobs,

       gauge_used_year=gauge_used_year,
       gauge_used_month=gauge_used_month,
       selected_year=selected_year,
       selected_month=selected_month,
    

       years=sorted(
    {
        row[0]
        for row in db.session.query(InformationRow.year).distinct().all()
    }
),

        months=list(range(1, 13)),
       month_names=calendar.month_name,
       changed_gauge_year=changed_gauge_year,
       changed_gauge_month=changed_gauge_month,
       current_year=today.year,
        current_month_name=today.strftime("%B"),
        upcoming_calibrations=upcoming_calibrations,

    )