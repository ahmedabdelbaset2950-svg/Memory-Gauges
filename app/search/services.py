from sqlalchemy import or_

from app.models.memory_gauge import MemoryGauge
from app.models.bundle_carrier import BundleCarrier
from app.models.battery import Battery
from app.models.jobs import Job
from app.models.information import InformationRow
from app.models.document import Document


def global_search(q):

    like = f"%{q}%"

    results = []

    # =============================
    # Memory Gauges
    # =============================

    for g in MemoryGauge.query.filter(
        or_(
            MemoryGauge.serial_number.ilike(like),
            MemoryGauge.company.ilike(like),
        )
    ).limit(5):

        results.append({
            "type": "Memory Gauge",
            "title": g.serial_number,
            "subtitle": g.company,
            "url": "/equipment"
        })

    # =============================
    # Bundle Carrier
    # =============================

    for b in BundleCarrier.query.filter(
        BundleCarrier.serial_number.ilike(like)
    ).limit(5):

        results.append({
            "type": "Bundle Carrier",
            "title": b.serial_number,
            "subtitle": "",
            "url": "/equipment"
        })

    # =============================
    # Battery
    # =============================

    for b in Battery.query.filter(
        Battery.serial_number.ilike(like)
    ).limit(5):

        results.append({
            "type": "Battery",
            "title": b.serial_number,
            "subtitle": "",
            "url": "/equipment?tab=batteries"
        })

    # =============================
    # Jobs
    # =============================

    for j in Job.query.filter(
        Job.well_number.ilike(like)
    ).limit(5):

        results.append({
            "type": "Job",
            "title": j.well_number,
            "subtitle": f"{j.day}/{j.month}/{j.year}",
            "url": f"/jobs?year={j.year}&month={j.month}"
        })

    # =============================
    # Information
    # =============================

    for i in InformationRow.query.filter(
        or_(
            InformationRow.well_number.ilike(like),
            InformationRow.gauge_serial.ilike(like),
            InformationRow.changed_to.ilike(like),
            InformationRow.engineer.ilike(like)
        )
    ).limit(5):

        results.append({
            "type": "Information",
            "title": i.well_number,
            "subtitle": i.gauge_serial,
            "url": f"/information?search={q}"
        })

    # =============================
    # Documents
    # =============================

    for d in Document.query.filter(
        or_(
            Document.title.ilike(like),
            Document.original_filename.ilike(like)
        )
    ).limit(5):

        results.append({
            "type": "Document",
            "title": d.title,
            "subtitle": d.original_filename,
            "url": "/documents"
        })

    return results