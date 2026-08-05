from flask import Blueprint
from app.models.app_settings import AppSettings

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings"
)

@settings_bp.app_context_processor
def inject_settings():
    settings = AppSettings.query.first()
    return dict(app_settings=settings)

from app.settings import routes
