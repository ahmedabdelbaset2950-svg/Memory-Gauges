from flask import Blueprint

equipment_bp = Blueprint(
    "equipment",
    __name__,
    template_folder="../templates"
)

from app.equipment import routes