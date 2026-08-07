import calendar
import io
import os
import uuid
from collections import defaultdict
from datetime import datetime

from flask import (
    Blueprint, render_template, request, jsonify, url_for,
    send_file, current_app
)
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.information import InformationRow, InformationMonth
from app.information.services import get_next_group_no, build_information_workbook
from app.information.services import import_information_excel
from app.users.decorators import admin_required
information = Blueprint(
    "information",
    __name__,
    url_prefix="/information"
)

UPLOAD_SUBDIR = os.path.join("static", "uploads", "information")


def _parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()
def create_year(year):

    for month in range(1, 13):

        exists = InformationMonth.query.filter_by(
            year=year,
            month=month
        ).first()

        if not exists:

            db.session.add(
                InformationMonth(
                    year=year,
                    month=month,
                    status="Open"
                )
            )

    db.session.commit()

@information.route("/")
@login_required
def index():

    year = request.args.get("year", 2026, type=int)
    month = request.args.get("month", 7, type=int)
    search = request.args.get("search", "", type=str).strip()

    # =====================================================
    # MONTHS
    # =====================================================

    months = (
        InformationMonth.query
        .order_by(
            InformationMonth.year.desc(),
            InformationMonth.month.asc()
        )
        .all()
    )

    # إنشاء أول شهر لو مفيش شهور
    # إنشاء السنة بالكامل إذا لم تكن موجودة
    create_year(year)

    months = (
    InformationMonth.query
    .order_by(
        InformationMonth.year.desc(),
        InformationMonth.month.asc()
    )
    .all()
)
    month_name = calendar.month_name[month]

    # =====================================================
    # CURRENT MONTH
    # =====================================================

    current_month = InformationMonth.query.filter_by(
        year=year,
        month=month
    ).first()

    is_closed = (
        current_month is not None
        and current_month.status == "Closed"
    )

    # =====================================================
    # INFORMATION ROWS
    # =====================================================

    rows_query = InformationRow.query

    if search:

        like = f"%{search}%"

        # البحث في كل الشهور والسنين
        rows_query = rows_query.filter(
            db.or_(
                InformationRow.well_number.ilike(like),
                InformationRow.gauge_serial.ilike(like),
                InformationRow.changed_to.ilike(like)
            )
        )

    else:

        # عرض الشهر الحالي فقط
        rows_query = rows_query.filter_by(
            year=year,
            month=month
        )

    # =====================================================
    # SORT JOBS BY ACTUAL FROM DATE
    # =====================================================

    rows = rows_query.order_by(

        InformationRow.year.desc(),
        InformationRow.month.desc(),

        # التاريخ هو أساس ترتيب الجوبات
        InformationRow.from_date.asc(),

        # يحافظ على صفوف نفس الجوب جنب بعض
        InformationRow.group_no.asc(),
        InformationRow.id.asc()

    ).all()

    # =====================================================
    # DISPLAY JOB NUMBER BASED ON DATE ORDER
    # =====================================================

    seen_groups = set()
    display_numbers = {}
    display_counter = 0

    for row in rows:

        group_key = (
            row.year,
            row.month,
            row.group_no
        )

        # أول Gauge في الـ Job
        if group_key not in seen_groups:

            display_counter += 1

            display_numbers[group_key] = display_counter

            row.is_group_start = True

            seen_groups.add(group_key)

        else:

            row.is_group_start = False

        # الرقم الظاهر فقط
        row.display_group_no = display_numbers[group_key]

        # اسم الشهر
        row.month_name_display = calendar.month_name[row.month]

    # =====================================================
    # SEARCH MODE
    # =====================================================

    is_global_search = bool(search)

    # =====================================================
    # ARCHIVE
    # =====================================================

    archive = defaultdict(list)

    for item in months:

        item.month_name = calendar.month_name[item.month]

        archive[item.year].append(item)

    # =====================================================
    # TEMPLATE
    # =====================================================

    return render_template(
        "information/information.html",
        rows=rows,
        month=month,
        year=year,
        month_name=month_name,
        archive=archive,
        is_closed=is_closed,
        search=search,
        is_global_search=is_global_search
    )


@information.route("/add-group", methods=["POST"])
@login_required
@admin_required
def add_group():

    data = request.get_json()

    year = data["year"]
    month = data["month"]

    group_no = get_next_group_no(year, month)

    created_rows = []

    for entry in data.get("rows", []):

        row = InformationRow(
            year=year,
            month=month,
            group_no=group_no,
            gauge_serial=entry.get("gauge_serial", "").strip(),
            from_date=_parse_date(entry.get("from_date")),
            to_date=_parse_date(entry.get("to_date")),
            days=entry.get("days") or 0,
            well_number=entry.get("well_number", "").strip(),
            changed_to=entry.get("changed_to", "").strip(),
            survey=entry.get("survey", "").strip(),
            position=entry.get("position", "").strip(),
            rig_name=entry.get("rig_name", "").strip(),
            bundle_carrier_sn=entry.get("bundle_carrier_sn", "").strip(),
            battery_sn=entry.get("battery_sn", "").strip(),
            engineer=entry.get("engineer", "").strip(),
            total_hours=entry.get("total_hours") or 0,
            total_samples=entry.get("total_samples") or 0,
            comment=entry.get("comment", "").strip()
        )

        db.session.add(row)
        created_rows.append(row)

    db.session.commit()

    return jsonify({
        "success": True,
        "group_no": group_no,
        "row_ids": [r.id for r in created_rows]
    })


@information.route("/row/<int:row_id>/update", methods=["POST"])
@login_required
def update_row(row_id):

    row = InformationRow.query.get_or_404(row_id)

    data = request.get_json()
    field = data.get("field")
    value = data.get("value", "")

    date_fields = {"from_date", "to_date"}
    float_fields = {"days", "total_hours"}
    integer_fields = {"total_samples"}

    allowed_fields = {
        "gauge_serial", "from_date", "to_date", "days", "well_number",
        "changed_to", "survey", "position", "rig_name", "bundle_carrier_sn",
        "battery_sn", "engineer", "total_hours", "total_samples", "comment"
    }

    if field not in allowed_fields:
        return jsonify({"success": False, "message": "Invalid field"}), 400

    if field in date_fields:
        setattr(row, field, _parse_date(value))

        # إعادة حساب عدد الأيام أوتوماتيك لو الفيلد تاريخ
        if row.from_date and row.to_date:
            row.days = (row.to_date - row.from_date).days + 1

    elif field in float_fields:
        try:
            setattr(row, field, float(value) if value != "" else 0)
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid number"
            }), 400

    elif field in integer_fields:
        try:
            setattr(row, field, int(value) if value != "" else 0)
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid integer"
            }), 400

    else:
        setattr(row, field, value.strip() if isinstance(value, str) else value)

    db.session.commit()

    return jsonify({
        "success": True,
        "days": row.days
    })


@information.route("/row/<int:row_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_row(row_id):

    row = InformationRow.query.get_or_404(row_id)

    db.session.delete(row)
    db.session.commit()

    return jsonify({"success": True})


@information.route("/row/<int:row_id>/attachment", methods=["POST"])
@login_required
@admin_required
def upload_attachment(row_id):

    row = InformationRow.query.get_or_404(row_id)

    file = request.files.get("file")

    if not file or file.filename == "":
        return jsonify({"success": False, "message": "No file provided"}), 400

    upload_dir = os.path.join(current_app.root_path, "..", UPLOAD_SUBDIR)
    upload_dir = os.path.abspath(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)

    original_name = secure_filename(file.filename)
    stored_name = f"{uuid.uuid4().hex}_{original_name}"

    file.save(os.path.join(upload_dir, stored_name))

    row.attachment_filename = stored_name
    row.attachment_original_name = original_name

    db.session.commit()

    return jsonify({
        "success": True,
        "attachment_name": original_name,
        "attachment_url": url_for("information.download_attachment", row_id=row.id)
    })


@information.route("/row/<int:row_id>/attachment/download")
@login_required
def download_attachment(row_id):

    row = InformationRow.query.get_or_404(row_id)

    if not row.attachment_filename:
        return jsonify({"success": False, "message": "No attachment"}), 404

    upload_dir = os.path.join(current_app.root_path, "..", UPLOAD_SUBDIR)
    upload_dir = os.path.abspath(upload_dir)

    return send_file(
        os.path.join(upload_dir, row.attachment_filename),
        as_attachment=True,
        download_name=row.attachment_original_name or row.attachment_filename
    )


@information.route("/close-month", methods=["POST"])
@login_required
@admin_required
def close_month():

    data = request.get_json()

    year = data["year"]
    month = data["month"]

    current = InformationMonth.query.filter_by(year=year, month=month).first()

    if current:
        current.status = "Closed"
        current.closed_at = datetime.utcnow()

    next_month = month + 1
    next_year = year

    if next_month > 12:
        next_month = 1
        next_year += 1

    # إنشاء شهور السنة الجديدة بالكامل
    create_year(next_year)

    existing_next = InformationMonth.query.filter_by(
    year=next_year,
    month=next_month
).first()

    if existing_next:
        existing_next.status = "Open"

    db.session.commit()

    return jsonify({
        "success": True,
        "next_month": next_month,
        "next_year": next_year,
        "redirect": url_for(
            "information.index",
            year=next_year,
            month=next_month
        )
    })


@information.route("/export")
@login_required
def export_excel():

    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    if not year or not month:
        return jsonify({
            "success": False,
            "message": "year and month are required"
        }), 400

    wb = build_information_workbook(year, month)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    month_name = calendar.month_name[month]

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Information_{month_name}_{year}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@information.route("/import", methods=["POST"])
@login_required
@admin_required
def import_information():

    try:
        print("========== IMPORT START ==========")

        print("FILES:", request.files)
        print("FORM :", request.form)

        file = request.files.get("file")

        print("FILE :", file)

        if file is None:
            return jsonify({
                "success": False,
                "message": "No file received."
            }), 400

        print("Filename:", file.filename)
        print("Content-Type:", file.content_type)

        # مهم جداً
        file.seek(0)

        print("Calling import_information_excel...")

        count = import_information_excel(file)

        print("Imported:", count)
        print("========== IMPORT END ==========")

        return jsonify({
            "success": True,
            "message": f"{count} rows imported successfully."
        })

    except Exception:
        import traceback
        traceback.print_exc()

        return jsonify({
            "success": False,
            "message": "Server Error أثناء استيراد الملف."
        }), 500
