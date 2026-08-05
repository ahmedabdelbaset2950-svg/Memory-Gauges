from flask import Blueprint, render_template, request, jsonify, url_for, send_file
from flask_login import login_required
from app.extensions import db
from app.models.memory_gauge import MemoryGauge
from app.models.bundle_carrier import BundleCarrier
from app.models.jobs import Job, JobColumn
from app.models.job_month import JobMonth
from app.jobs.services import get_worked_days, get_month_days, build_jobs_workbook
from datetime import datetime
import calendar
import io
from collections import defaultdict
from flask import jsonify
import pandas as pd




jobs = Blueprint(
    "jobs",
    __name__,
    url_prefix="/jobs"
)
from werkzeug.utils import secure_filename
import os
import pandas as pd

def create_year(year):

    for month in range(1, 13):

        exists = JobMonth.query.filter_by(
            year=year,
            month=month
        ).first()

        if not exists:

            db.session.add(
                JobMonth(
                    year=year,
                    month=month,
                    status="Open"
                )
            )

    db.session.commit()
@jobs.route("/")
@login_required
def index():

    year = request.args.get("year", 2026, type=int)
    month = request.args.get("month", 7, type=int)

    gauges = (
        MemoryGauge.query
        .order_by(MemoryGauge.serial_number)
        .all()
    )

    bundles = (
        BundleCarrier.query
        .order_by(BundleCarrier.serial_number)
        .all()
    )

    columns = (
        JobColumn.query
        .filter_by(month=month, year=year)
        .order_by(JobColumn.id)
        .all()
    )
    saved_jobs = (
    Job.query
    .filter_by(
        year=year,
        month=month
    )
    .all()
)

    # إنشاء أول شهر إذا لم يكن موجوداً
    months = (
        JobMonth.query
        .order_by(JobMonth.year.desc(), JobMonth.month.asc())
        .all()
    )

    create_year(year)
    months = (
    JobMonth.query
    .order_by(JobMonth.year.desc(), JobMonth.month.asc())
    .all()
)

    month_name = calendar.month_name[month]

    # حالة الشهر الحالي
    current_month = JobMonth.query.filter_by(
        year=year,
        month=month
    ).first()

    is_closed = (
        current_month is not None
        and current_month.status == "Closed"
    )

    # حساب Worked Days
    for gauge in gauges:
        gauge.worked_days = get_worked_days(
            equipment_type="gauge",
            equipment_id=gauge.id,
            month=month,
            year=year
        )

    for bundle in bundles:
        bundle.worked_days = get_worked_days(
            equipment_type="bundle",
            equipment_id=bundle.id,
            month=month,
            year=year
        )

    # تجهيز الأرشيف
    archive = defaultdict(list)

    for item in months:
        item.month_name = calendar.month_name[item.month]
        archive[item.year].append(item)
        jobs_map = {}

    for job in saved_jobs:
        jobs_map[
        (
            job.day,
            job.equipment_type,
            job.equipment_id
        )
    ] = job

    month_days = get_month_days(year, month)

    return render_template(
    "jobs/jobs.html",
    gauges=gauges,
    bundles=bundles,
    columns=columns,
    month=month,
    year=year,
    month_name=month_name,
    archive=archive,
    is_closed=is_closed,
    jobs_map=jobs_map,
    month_days=month_days
)

@jobs.route("/save", methods=["POST"])
@login_required
def save_job():

    data = request.get_json()

    well_number = (data.get("well_number") or "").strip()

    # نجيب كل الصفوف المطابقة (مش صف واحد بس) عشان نلغي أي تكرار قديم
    existing_rows = Job.query.filter_by(
        year=data["year"],
        month=data["month"],
        day=data["day"],
        equipment_type=data["equipment_type"],
        equipment_id=data["equipment_id"]
    ).all()

    if well_number == "":

        # مسح القيمة = حذف كل الصفوف المطابقة (لو فيه تكرار قديم يتحذف برضه)
        for row in existing_rows:
            db.session.delete(row)

        db.session.commit()

        worked_days = get_worked_days(
            data["equipment_type"],
            data["equipment_id"],
            data["month"],
            data["year"]
        )

        return jsonify({
    "success": True,
    "imported": len(jobs),
    "year": min(y for y, m in months_to_delete),
    "month": min(m for y, m in months_to_delete)
})

    if existing_rows:

        # نعدّل أول صف، ونحذف أي صفوف مكررة تانية لنفس اليوم
        job = existing_rows[0]
        job.well_number = well_number

        for duplicate in existing_rows[1:]:
            db.session.delete(duplicate)

    else:

        job = Job(
            year=data["year"],
            month=data["month"],
            day=data["day"],
            well_number=well_number,
            equipment_type=data["equipment_type"],
            equipment_id=data["equipment_id"]
        )

        db.session.add(job)

    db.session.commit()

    worked_days = get_worked_days(
        job.equipment_type,
        job.equipment_id,
        job.month,
        job.year
    )

    return jsonify({
        "success": True,
        "job_id": job.id,
        "worked_days": worked_days
    })

@jobs.route("/add-column", methods=["POST"])
@login_required
def add_column():

    data = request.get_json()

    column = JobColumn(
        name=data["name"],
        equipment_type=data["equipment_type"],
        month=data["month"],
        year=data["year"]
    )

    db.session.add(column)
    db.session.commit()

    return jsonify({
        "success": True,
        "id": column.id,
        "name": column.name
    })
@jobs.route("/close-month", methods=["POST"])
@login_required
def close_month():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No JSON received"
        }), 400

    year = int(data["year"])
    month = int(data["month"])

    current = JobMonth.query.filter_by(
        year=year,
        month=month
    ).first()

    if current:

        current.status = "Closed"
        current.closed_at = datetime.utcnow()

    else:

        current = JobMonth(
            year=year,
            month=month,
            status="Closed",
            closed_at=datetime.utcnow()
        )

        db.session.add(current)

    # إنشاء الشهر التالي

    next_month = month + 1
    next_year = year

    if next_month > 12:

        next_month = 1
        next_year += 1

        # إنشاء السنة الجديدة بالكامل
        create_year(next_year)

    exists = JobMonth.query.filter_by(
        year=next_year,
        month=next_month
    ).first()

    if exists:
        exists.status = "Open"

    db.session.commit()

    return jsonify({
        "success": True,
        "next_month": next_month,
        "next_year": next_year,
        "redirect": url_for(
            "jobs.index",
            year=next_year,
            month=next_month
        )
    })


@jobs.route("/export")
@login_required
def export_excel():

    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    if not year or not month:
        return jsonify({
            "success": False,
            "message": "year and month are required"
        }), 400

    wb = build_jobs_workbook(year, month)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    month_name = calendar.month_name[month]

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Jobs_{month_name}_{year}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@jobs.route("/import-preview", methods=["POST"])
@login_required
def import_preview():

    print("STEP 1")

    file = request.files.get("excel_file")

    print("STEP 2")

    try:
        print("STEP 3")

        excel = pd.ExcelFile(file)
        sheet = excel.sheet_names[0]
        df = pd.read_excel(
            excel,
            sheet_name=excel.sheet_names[0],
            header=None
           
        ).fillna("")
   

        print("STEP 4")

        df = df.fillna("")

        print("STEP 5")

        return jsonify({
            "success": True,
            "columns": df.columns.tolist(),
            "rows": df.head(20).to_dict("records"),
            "total": len(df)
        })

    except Exception as e:
        print("ERROR:", repr(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@jobs.route("/import", methods=["POST"])
@login_required
def import_jobs():

    file = request.files.get("excel_file")

    if not file:
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    try:

        excel = pd.ExcelFile(file)

        df = pd.read_excel(
            excel,
            sheet_name=excel.sheet_names[0],
            header=8
        ).fillna("")

        # تنظيف أسماء الأعمدة
        df.columns = df.columns.str.strip()
        df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        df = df[df["Data"].notna()].reset_index(drop=True)


        # تجهيز الأجهزة
        gauges = {
            g.serial_number.strip().upper(): g
            for g in MemoryGauge.query.all()
        }

        bundles = {
            b.serial_number.strip().upper(): b
            for b in BundleCarrier.query.all()
        }

        # الأعمدة الخاصة بالأجهزة فقط
        equipment_columns = df.columns[3:]

        # معرفة الشهور الموجودة داخل الملف
        months_to_delete = set()

        for value in df["Data"]:

            if value == "":
                continue

            date = pd.to_datetime(value)

            months_to_delete.add(
                (date.year, date.month)
            )

        # حذف البيانات القديمة
        for year, month in months_to_delete:

            Job.query.filter_by(
                year=year,
                month=month
            ).delete()

        db.session.commit()

        jobs = []

        # إنشاء السجلات
        for _, row in df.iterrows():

            if row["Data"] == "":
                continue

            date = pd.to_datetime(row["Data"])

            for serial in equipment_columns:

                well = str(row[serial]).strip()

                if not well:
                    continue

                serial = str(serial).strip().upper()

                if serial in gauges:

                    jobs.append(
                        Job(
                            year=date.year,
                            month=date.month,
                            day=date.day,
                            well_number=well,
                            equipment_type="gauge",
                            equipment_id=gauges[serial].id
                        )
                    )

                elif serial in bundles:

                    jobs.append(
                        Job(
                            year=date.year,
                            month=date.month,
                            day=date.day,
                            well_number=well,
                            equipment_type="bundle",
                            equipment_id=bundles[serial].id
                        )
                    )

        db.session.bulk_save_objects(jobs)
        db.session.commit()

        return jsonify({
            "success": True,
            "imported": len(jobs)
        })

    except Exception as e:

        db.session.rollback()

        print(e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500