from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    BooleanField,
    SelectField,
    TextAreaField,
    SubmitField,
    DateField,
    DecimalField
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional
)


# ==========================================================
# Memory Gauge Form
# ==========================================================

class MemoryGaugeForm(FlaskForm):

    serial_number = StringField(
        "Serial Number",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    company = StringField(
        "Company",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    gauge_type = StringField(
        "Gauge Type",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    # ======================================
    # Bundle Compatibility
    # ======================================

    supports_dual = BooleanField(
        "Supports Dual"
    )

    dual_type = SelectField(
        "Dual Compatibility",
    choices=[
        ("Internal", "Internal"),
        ("External", "External"),
        ("Both", "Both")

        ],

        default="Both"
    )

    supports_quad = BooleanField(
        "Supports Quad"
    )

    quad_type = SelectField(
        "Quad Compatibility",
    choices=[
        ("Internal", "Internal"),
        ("External", "External"),
        ("Both", "Both")
        ],
        default="Both"
   )
    # ==========================

    calibration_date = DateField(
        "Calibration Date",
        format="%Y-%m-%d",
        validators=[],
        default=None
    )

    battery_serial = StringField(
        "Battery Serial",
        validators=[
            Length(max=100)
        ]
    )

    status = SelectField(

        "Status",

        choices=[

            ("Available", "Available"),

            ("In Use", "In Use"),

            ("Maintenance", "Maintenance"),

            ("Calibration", "Calibration"),

            ("Retired", "Retired")

        ]

    )

    notes = TextAreaField(
        "Notes"
    )

    submit = SubmitField(
        "Save"
    )


# ==========================================================
# Bundle Carrier Form
# ==========================================================

class BundleCarrierForm(FlaskForm):

    serial_number = StringField(

        "Serial Number",

        validators=[

            DataRequired(),

            Length(max=100)

        ]

    )

    company = StringField(

        "Company",

        validators=[

            DataRequired(),

            Length(max=100)

        ]

    )

    type = SelectField(

        "Type",

        choices=[

            ("Internal", "Internal"),

            ("External", "External"),

            ("Internal / External", "Internal / External")

        ]

    )

    position = SelectField(

        "Position",

        choices=[

            ("Dual", "Dual"),

            ("Quad", "Quad")

        ]

    )
    pressure_test_date = DateField(
    "Last Pressure Test",
    format="%Y-%m-%d",
    validators=[Optional()]
    )

    current_location = StringField(

        "Current Location"

    )

    allen_key = StringField(

        "Allen Key"

    )

    notes = TextAreaField(

        "Notes"

    )

    submit = SubmitField(

        "Save"

    )

# ==========================================================
# Battery Form
# ==========================================================

class BatteryForm(FlaskForm):

    serial_number = StringField(
        "Serial Number",
        validators=[
            DataRequired(),
            Length(max=120)
        ]
    )

    compatible_gauge_type = StringField(
        "Compatible Gauge Type",
        validators=[
            DataRequired(),
            Length(max=120)
        ]
    )

    # ======================================================
    # Battery Capacity
    # ======================================================

    capacity = DecimalField(
        "Capacity",
        validators=[DataRequired()],
        places=3
    )

    capacity_unit = SelectField(
        "Unit",
        choices=[
            ("Ah", "Ah"),
            ("mAh", "mAh"),
            ("D", "D")
        ],
        validators=[DataRequired()]
    )

    # ======================================================
    # Previous Consumption
    # الاستهلاك قبل بداية تسجيل البطارية على MGMS
    # ======================================================

    previous_consumption = DecimalField(
        "Previous Consumption",
        places=4,
        default=0
    )

    # ======================================================
    # Status
    # ======================================================

    status = SelectField(
        "Status",
        choices=[
            ("Available", "Available"),
            ("In Use", "In Use"),
            ("Low", "Low"),
            ("Retired", "Retired")
        ]
    )

    notes = TextAreaField(
        "Notes"
    )

    submit = SubmitField(
        "Save"
    )