from app.extensions import db

from app.models.memory_gauge import MemoryGauge
from app.models.bundle_carrier import BundleCarrier


# ==========================================================
# Memory Gauge Services
# ==========================================================

def get_all_memory_gauges():

    return MemoryGauge.query.order_by(
        MemoryGauge.serial_number.asc()
    ).all()


def get_memory_gauge(gauge_id):

    return MemoryGauge.query.get_or_404(
        gauge_id
    )


def create_memory_gauge(form):

    gauge = MemoryGauge(

    serial_number=form.serial_number.data,

    company=form.company.data,

    gauge_type=form.gauge_type.data,

    supports_dual=form.supports_dual.data,

    dual_type=form.dual_type.data,

    supports_quad=form.supports_quad.data,

    quad_type=form.quad_type.data,

    calibration_date=form.calibration_date.data,

    battery_serial=form.battery_serial.data,

    status=form.status.data,

    notes=form.notes.data

)

    db.session.add(gauge)

    db.session.commit()

    return gauge


def update_memory_gauge(gauge, form):

    gauge.serial_number = form.serial_number.data

    gauge.company = form.company.data

    gauge.gauge_type = form.gauge_type.data

    gauge.supports_dual = form.supports_dual.data

    gauge.dual_type = form.dual_type.data

    gauge.supports_quad = form.supports_quad.data

    gauge.quad_type = form.quad_type.data

    gauge.calibration_date = form.calibration_date.data

    gauge.battery_serial = form.battery_serial.data

    gauge.status = form.status.data

    gauge.notes = form.notes.data

    db.session.commit()

    return gauge


def delete_memory_gauge(gauge):

    db.session.delete(gauge)

    db.session.commit()


# ==========================================================
# Bundle Carrier Services
# ==========================================================

def get_all_bundle_carriers():

    return BundleCarrier.query.order_by(
        BundleCarrier.serial_number.asc()
    ).all()


def get_bundle_carrier(bundle_id):

    return BundleCarrier.query.get_or_404(
        bundle_id
    )


def create_bundle_carrier(form):

    bundle = BundleCarrier(

        serial_number=form.serial_number.data,

        company=form.company.data,

        type=form.type.data,

        position=form.position.data,
        pressure_test_date=form.pressure_test_date.data,

        current_location=form.current_location.data,

        allen_key=form.allen_key.data,

        notes=form.notes.data

    )

    db.session.add(bundle)

    db.session.commit()

    return bundle


def update_bundle_carrier(bundle, form):

    bundle.serial_number = form.serial_number.data

    bundle.company = form.company.data

    bundle.type = form.type.data

    bundle.position = form.position.data
    bundle.pressure_test_date = form.pressure_test_date.data

    bundle.current_location = form.current_location.data

    bundle.allen_key = form.allen_key.data

    bundle.notes = form.notes.data

    db.session.commit()

    return bundle


def delete_bundle_carrier(bundle):

    db.session.delete(bundle)

    db.session.commit()

# ==========================================================
# Battery Services
# ==========================================================

from app.models.battery import Battery


def get_all_batteries():
    return Battery.query.order_by(
        Battery.serial_number.asc()
    ).all()


def get_battery(battery_id):
    return Battery.query.get_or_404(battery_id)


# ==========================================================
# Create Battery
# ==========================================================

def create_battery(form):

    battery = Battery(

        serial_number=form.serial_number.data,

        compatible_gauge_type=form.compatible_gauge_type.data,

        capacity=float(form.capacity.data),

        capacity_unit=form.capacity_unit.data,

        # الاستهلاك السابق قبل استخدام MGMS
        previous_consumption=float(
            form.previous_consumption.data or 0
        ),

        status=form.status.data,

        notes=form.notes.data
    )

    db.session.add(battery)
    db.session.commit()

    return battery


# ==========================================================
# Update Battery
# ==========================================================

def update_battery(battery, form):

    battery.serial_number = form.serial_number.data

    battery.compatible_gauge_type = (
        form.compatible_gauge_type.data
    )

    battery.capacity = float(
        form.capacity.data
    )

    battery.capacity_unit = (
        form.capacity_unit.data
    )

    # نقدر نعدل الاستهلاك السابق يدويًا
    battery.previous_consumption = float(
        form.previous_consumption.data or 0
    )

    battery.status = form.status.data

    battery.notes = form.notes.data

    db.session.commit()

    return battery


# ==========================================================
# Delete Battery
# ==========================================================

def delete_battery(battery):

    db.session.delete(battery)

    db.session.commit()