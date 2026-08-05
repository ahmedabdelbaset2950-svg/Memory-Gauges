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
