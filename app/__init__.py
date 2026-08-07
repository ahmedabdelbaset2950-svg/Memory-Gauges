from flask import Flask
import os
from config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # ===========================
    # Extensions
    # ===========================

    db.init_app(app)

    migrate.init_app(app, db)

    login_manager.init_app(app)

    csrf.init_app(app)

    # ===========================
    # Blueprints
    # ===========================

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.equipment import equipment_bp
    app.register_blueprint(equipment_bp)

    from app.jobs import jobs_bp
    app.register_blueprint(jobs_bp)
    from app.information import information_bp
    app.register_blueprint(information_bp)

    from app.documents import documents_bp
    app.register_blueprint(documents_bp)

    from app.reports import reports_bp
    app.register_blueprint(reports_bp)
    from app.users import users_bp
    app.register_blueprint(users_bp)

    from app.settings import settings_bp
    app.register_blueprint(settings_bp)

    from app.search import search_bp
    app.register_blueprint(search_bp)
    

    # ===========================
    # Models
    # ===========================

    from app.models import (
        User,
        MemoryGauge,
        BundleCarrier,
        Battery,
        Job,
        MaintenanceRecord,
        Document,
        AppSettings

    )

    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(int(user_id))

    @app.context_processor
    def inject_settings():
        settings = AppSettings.query.first()
        if settings is None:
            settings = AppSettings()
        return dict(app_settings=settings)
    
    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all() 
    return app
