from datetime import date, timedelta

from app.extensions import db
from app.models.battery import Battery
from app.models.battery_cycle import BatteryCycle
from app.models.information import InformationRow
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request
)


from flask_login import login_required

from app.users.decorators import admin_required

from app.equipment import equipment_bp

from app.equipment.forms import (
    MemoryGaugeForm,
    BundleCarrierForm,
    BatteryForm
)
from flask import request
from app.equipment.services import (

    get_all_memory_gauges,
    get_memory_gauge,
    create_memory_gauge,
    update_memory_gauge,
    delete_memory_gauge,

    get_all_bundle_carriers,
    get_bundle_carrier,
    create_bundle_carrier,
    update_bundle_carrier,
    delete_bundle_carrier,

    get_all_batteries,
    get_battery,
    create_battery,
    update_battery,
    delete_battery

)


# ==========================================================
# Equipment Dashboard
# ==========================================================

@equipment_bp.route("/equipment")
@login_required
def equipment():

    gauge_form = MemoryGaugeForm()

    bundle_form = BundleCarrierForm()

    battery_form = BatteryForm()

    memory_gauges = get_all_memory_gauges()

    bundle_carriers = get_all_bundle_carriers()

    batteries = get_all_batteries()

    open_type = request.args.get("open")

    return render_template(

        "equipment/equipment.html",

        gauge_form=gauge_form,

        bundle_form=bundle_form,

        battery_form=battery_form,

        memory_gauges=memory_gauges,

        bundle_carriers=bundle_carriers,

        batteries=batteries,

        open_type=open_type

    )

# ==========================================================
# Add Memory Gauge
# ==========================================================

@equipment_bp.route(
    "/memory-gauges/add",
    methods=["POST"]
)
@login_required
@admin_required
def add_memory_gauge():

    form = MemoryGaugeForm()

    if form.validate_on_submit():

        create_memory_gauge(form)

        flash(

            "Memory Gauge created successfully.",

            "success"

        )

    else:

        flash(

            "Please complete all required fields.",

            "danger"

        )

    return redirect(
        url_for("equipment.equipment")
    )


# ==========================================================
# Edit Memory Gauge
# ==========================================================

@equipment_bp.route(
    "/memory-gauges/<int:gauge_id>/edit",
    methods=["POST"]
)
@login_required
@admin_required
def edit_memory_gauge(gauge_id):

    gauge = get_memory_gauge(gauge_id)

    form = MemoryGaugeForm()

    if form.validate_on_submit():

        update_memory_gauge(gauge, form)

        flash(
            "Memory Gauge updated successfully.",
            "success"
        )

    else:

        flash(
            "Please complete all required fields.",
            "danger"
        )

    return redirect(
        url_for("equipment.equipment")
    )


# ==========================================================
# Delete Memory Gauge
# ==========================================================

@equipment_bp.route(
    "/memory-gauges/<int:gauge_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def remove_memory_gauge(gauge_id):

    gauge = get_memory_gauge(gauge_id)

    delete_memory_gauge(gauge)

    flash(

        "Memory Gauge deleted successfully.",

        "success"

    )

    return redirect(
        url_for("equipment.equipment")
    )


# ==========================================================
# Add Bundle Carrier
# ==========================================================

@equipment_bp.route(
    "/bundle-carriers/add",
    methods=["POST"]
)
@login_required
@admin_required
def add_bundle_carrier():

    form = BundleCarrierForm()

    if form.validate_on_submit():

        create_bundle_carrier(form)

        flash(

            "Bundle Carrier created successfully.",

            "success"

        )

    else:

        flash(

            "Please complete all required fields.",

            "danger"

        )

    return redirect(
        url_for("equipment.equipment")
    )


# ==========================================================
# Edit Bundle Carrier
# ==========================================================

@equipment_bp.route(
    "/bundle-carriers/<int:bundle_id>/edit",
    methods=["POST"]
)
@login_required
@admin_required
def edit_bundle_carrier(bundle_id):

    bundle = get_bundle_carrier(bundle_id)

    form = BundleCarrierForm()

    if form.validate_on_submit():

        update_bundle_carrier(bundle, form)

        flash(
            "Bundle Carrier updated successfully.",
            "success"
        )

    else:

        flash(
            "Please complete all required fields.",
            "danger"
        )

    return redirect(
        url_for("equipment.equipment")
    )


# ==========================================================
# Delete Bundle Carrier
# ==========================================================

@equipment_bp.route(
    "/bundle-carriers/<int:bundle_id>/delete",
    methods=["POST"]
)
@login_required
@admin_required
def remove_bundle_carrier(bundle_id):

    bundle = get_bundle_carrier(bundle_id)

    delete_bundle_carrier(bundle)

    flash(

        "Bundle Carrier deleted successfully.",

        "success"

    )

    return redirect(
        url_for("equipment.equipment")
    )

# ==========================================================
# Batteries
# ==========================================================

@equipment_bp.route("/batteries/add", methods=["POST"])
@login_required
@admin_required
def add_battery():
    form = BatteryForm()
    if form.validate_on_submit():
        create_battery(form)
        flash("Battery created successfully.", "success")
    else:
        flash("Please complete all required battery fields.", "danger")
    return redirect(url_for("equipment.equipment"))


@equipment_bp.route("/batteries/<int:battery_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_battery(battery_id):
    battery = get_battery(battery_id)
    form = BatteryForm()
    if form.validate_on_submit():
        update_battery(battery, form)
        flash("Battery updated successfully.", "success")
    else:
        flash("Please complete all required battery fields.", "danger")
    return redirect(url_for("equipment.equipment"))


@equipment_bp.route("/batteries/<int:battery_id>/delete", methods=["POST"])
@login_required
@admin_required
def remove_battery(battery_id):
    battery = get_battery(battery_id)
    delete_battery(battery)
    flash("Battery deleted successfully.", "success")
    return redirect(url_for("equipment.equipment"))

@equipment_bp.route(
    "/batteries/<int:battery_id>/start-cycle",
    methods=["POST"]
)
@login_required
@admin_required
def start_battery_cycle(battery_id):
    battery = get_battery(battery_id)

    if not battery:
        flash("Battery not found.", "danger")
        return redirect(url_for("equipment.equipment"))

    today = date.today()

    active_cycle = (
        BatteryCycle.query
        .filter_by(
            battery_id=battery.id,
            ended_on=None
        )
        .order_by(BatteryCycle.cycle_number.desc())
        .first()
    )

    # منع إنشاء دورتين بتاريخ البداية نفسه،
    # لأن سجلات Information تعتمد على التاريخ.
    if active_cycle and active_cycle.started_on >= today:
        flash(
            "A new cycle has already started today. "
            "The current cycle was not changed.",
            "warning"
        )
        return redirect(url_for("equipment.equipment"))

    # إغلاق الدورة الحالية في نهاية أمس.
    if active_cycle:
        active_cycle.ended_on = today - timedelta(days=1)

    else:
        # أول مرة: نحفظ السجلات القديمة ضمن دورة تاريخية.
        last_cycle = (
            BatteryCycle.query
            .filter_by(battery_id=battery.id)
            .order_by(BatteryCycle.cycle_number.desc())
            .first()
        )

        if last_cycle is None:
            first_usage = (
                db.session.query(
                    db.func.min(InformationRow.from_date)
                )
                .filter(
                    db.func.trim(InformationRow.battery_sn)
                    == battery.serial_number.strip(),
                    InformationRow.from_date.isnot(None)
                )
                .scalar()
            )

            if first_usage and first_usage < today:
                db.session.add(
                    BatteryCycle(
                        battery_id=battery.id,
                        cycle_number=1,
                        started_on=first_usage,
                        ended_on=today - timedelta(days=1)
                    )
                )
                next_cycle_number = 2
            else:
                next_cycle_number = 1
        else:
            next_cycle_number = last_cycle.cycle_number + 1

    # إنشاء الدورة الجديدة من اليوم.
    db.session.add(
        BatteryCycle(
            battery_id=battery.id,
            cycle_number=next_cycle_number,
            started_on=today,
            ended_on=None
        )
    )

    try:
        db.session.commit()
        flash(
            f"New consumption cycle started for battery "
            f"{battery.serial_number}.",
            "success"
        )
    except Exception:
        db.session.rollback()
        flash(
            "Could not start the new battery cycle.",
            "danger"
        )

    return redirect(url_for("equipment.equipment"))

