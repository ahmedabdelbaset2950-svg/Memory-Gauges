import os
import uuid
from datetime import datetime, date
from collections import defaultdict

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    jsonify, send_from_directory, current_app, flash
)
from flask_login import login_required, current_user

try:
    from werkzeug.utils import secure_filename
except ImportError:  # pragma: no cover - fallback for older Werkzeug installs
    from werkzeug import secure_filename

from app.extensions import db
from app.models.document import Document, CATEGORY_CHOICES
from app.models.memory_gauge import MemoryGauge
from app.models.bundle_carrier import BundleCarrier

documents = Blueprint(
    "documents",
    __name__,
    url_prefix="/documents"
)

UPLOAD_SUBDIR = os.path.join("static", "uploads", "documents")


def _upload_dir():
    upload_dir = os.path.join(current_app.root_path, "..", UPLOAD_SUBDIR)
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def _icon_for_ext(ext):

    ext = (ext or "").lower()

    if ext in ("pdf",):
        return "bi-file-earmark-pdf-fill", "#DC2626"

    if ext in ("jpg", "jpeg", "png", "gif", "webp"):
        return "bi-file-earmark-image-fill", "#2563EB"

    if ext in ("xlsx", "xls", "csv"):
        return "bi-file-earmark-excel-fill", "#16A34A"

    if ext in ("doc", "docx"):
        return "bi-file-earmark-word-fill", "#1D4ED8"

    return "bi-file-earmark-fill", "#64748B"


def _expiry_status(expiry_date):

    if not expiry_date:
        return None

    days_left = (expiry_date - date.today()).days

    if days_left < 0:
        return "expired"

    if days_left <= 30:
        return "expiring"

    return "valid"


@documents.route("/")
@login_required
def index():

    category = request.args.get("category", "")
    search = request.args.get("search", "").strip()
    equipment_type = request.args.get("equipment_type", "")
    equipment_id = request.args.get("equipment_id", type=int)

    query = Document.query

    if category:
        query = query.filter_by(category=category)

    if equipment_type and equipment_id:
        query = query.filter_by(
            equipment_type=equipment_type,
            equipment_id=equipment_id
        )

    if search:
        like = f"%{search}%"
        query = query.filter(Document.title.ilike(like))

    docs = query.order_by(Document.created_at.desc()).all()

    # لو البحث برقم سريال، نلاقي المعدات المطابقة ونضيف مستنداتها
    if search:

        matched_gauges = MemoryGauge.query.filter(
            MemoryGauge.serial_number.ilike(f"%{search}%")
        ).all()

        matched_bundles = BundleCarrier.query.filter(
            BundleCarrier.serial_number.ilike(f"%{search}%")
        ).all()

        extra_pairs = (
            [("gauge", g.id) for g in matched_gauges]
            + [("bundle", b.id) for b in matched_bundles]
        )

        if extra_pairs:

            conditions = [
                db.and_(
                    Document.equipment_type == etype,
                    Document.equipment_id == eid
                )
                for etype, eid in extra_pairs
            ]

            extra_docs = Document.query.filter(db.or_(*conditions)).all()

            existing_ids = {d.id for d in docs}

            for doc in extra_docs:
                if doc.id not in existing_ids:
                    docs.append(doc)
                    existing_ids.add(doc.id)

            docs.sort(key=lambda d: d.created_at, reverse=True)

    # عدّاد لكل تصنيف (للسايد بار)
    category_counts = defaultdict(int)

    for d in Document.query.all():
        category_counts[d.category] += 1

    # خرائط سريعة لأسماء المعدات المرتبطة
    gauges_map = {g.id: g.serial_number for g in MemoryGauge.query.all()}
    bundles_map = {b.id: b.serial_number for b in BundleCarrier.query.all()}

    doc_items = []

    for d in docs:

        icon, color = _icon_for_ext(d.file_ext)

        equipment_label = None

        if d.equipment_type == "gauge" and d.equipment_id in gauges_map:
            equipment_label = f"Gauge · {gauges_map[d.equipment_id]}"
        elif d.equipment_type == "bundle" and d.equipment_id in bundles_map:
            equipment_label = f"Bundle · {bundles_map[d.equipment_id]}"

        doc_items.append({
            "doc": d,
            "icon": icon,
            "color": color,
            "equipment_label": equipment_label,
            "expiry_status": _expiry_status(d.expiry_date)
        })

    all_gauges = MemoryGauge.query.order_by(MemoryGauge.serial_number).all()
    all_bundles = BundleCarrier.query.order_by(BundleCarrier.serial_number).all()

    return render_template(
        "documents/documents.html",
        documents=doc_items,
        categories=CATEGORY_CHOICES,
        category_counts=category_counts,
        active_category=category,
        search=search,
        all_gauges=all_gauges,
        all_bundles=all_bundles,
        total_docs=len(Document.query.all())
    )


@documents.route("/upload", methods=["POST"])
@login_required
def upload():

    file = request.files.get("file")

    if not file or file.filename == "":
        flash("Please choose a file to upload.", "warning")
        return redirect(url_for("documents.index"))

    title = request.form.get("title", "").strip()
    category = request.form.get("category", "other")
    equipment_type = request.form.get("equipment_type", "").strip()
    equipment_id = request.form.get("equipment_id", type=int)
    expiry_date_raw = request.form.get("expiry_date", "").strip()
    notes = request.form.get("notes", "").strip()

    if not title:
        title = secure_filename(file.filename).rsplit(".", 1)[0]

    original_name = secure_filename(file.filename)
    ext = original_name.rsplit(".", 1)[-1] if "." in original_name else ""
    stored_name = f"{uuid.uuid4().hex}_{original_name}"

    file.save(os.path.join(_upload_dir(), stored_name))

    expiry_date = None

    if expiry_date_raw:
        try:
            expiry_date = datetime.strptime(expiry_date_raw, "%Y-%m-%d").date()
        except ValueError:
            expiry_date = None

    doc = Document(
        title=title,
        category=category,
        equipment_type=equipment_type if equipment_type in ("gauge", "bundle") else None,
        equipment_id=equipment_id if equipment_type in ("gauge", "bundle") else None,
        file_filename=stored_name,
        original_filename=original_name,
        file_ext=ext,
        expiry_date=expiry_date,
        notes=notes,
        uploaded_by=getattr(current_user, "username", None)
    )

    db.session.add(doc)
    db.session.commit()

    flash("Document uploaded successfully.", "success")

    return redirect(url_for("documents.index"))


@documents.route("/<int:doc_id>/download")
@login_required
def download(doc_id):

    doc = Document.query.get_or_404(doc_id)

    return send_from_directory(
        _upload_dir(),
        doc.file_filename,
        as_attachment=True,
        download_name=doc.original_filename
    )


@documents.route("/<int:doc_id>/delete", methods=["POST"])
@login_required
def delete(doc_id):

    doc = Document.query.get_or_404(doc_id)

    try:
        os.remove(os.path.join(_upload_dir(), doc.file_filename))
    except OSError:
        pass

    db.session.delete(doc)
    db.session.commit()

    return jsonify({"success": True})


@documents.route("/<int:doc_id>/update", methods=["POST"])
@login_required
def update(doc_id):

    doc = Document.query.get_or_404(doc_id)
    data = request.get_json() or {}

    field = data.get("field")
    value = data.get("value", "")

    if field == "title":
        doc.title = value.strip()

    elif field == "category":
        doc.category = value

    elif field == "expiry_date":
        doc.expiry_date = (
            datetime.strptime(value, "%Y-%m-%d").date() if value else None
        )

    elif field == "notes":
        doc.notes = value.strip()

    else:
        return jsonify({"success": False, "message": "Unknown field"}), 400

    db.session.commit()

    return jsonify({
        "success": True,
        "expiry_status": _expiry_status(doc.expiry_date)
    })
