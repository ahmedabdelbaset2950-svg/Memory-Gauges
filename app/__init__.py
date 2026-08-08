from flask import Flask, jsonify
from flask_login import login_required
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
@app.route("/admin/migrate-local-database")
@login_required
def migrate_local_database():

    from sqlalchemy import create_engine, MetaData, select, text

    try:

        # ==========================================
        # SQLite database
        # ==========================================

        sqlite_path = os.path.join(
            app.instance_path,
            "mgms.db"
        )

        if not os.path.exists(sqlite_path):
            return jsonify({
                "success": False,
                "message": f"SQLite database not found: {sqlite_path}"
            }), 404

        sqlite_engine = create_engine(
            f"sqlite:///{sqlite_path}"
        )

        # ==========================================
        # Load SQLite tables
        # ==========================================

        sqlite_metadata = MetaData()
        sqlite_metadata.reflect(
            bind=sqlite_engine
        )

        # PostgreSQL tables
        postgres_metadata = MetaData()
        postgres_metadata.reflect(
            bind=db.engine
        )

        sqlite_conn = sqlite_engine.connect()
        postgres_conn = db.engine.connect()

        # ==========================================
        # Find tables
        # ==========================================

        results = []

        for table_name, sqlite_table in sqlite_metadata.tables.items():

            print(
                f"MIGRATION: {table_name}"
            )

            postgres_table = (
                postgres_metadata.tables.get(
                    table_name
                )
            )

            if postgres_table is None:

                results.append({
                    "table": table_name,
                    "status": "skipped",
                    "reason": "Table does not exist in PostgreSQL"
                })

                continue

            # Read SQLite data
            rows = sqlite_conn.execute(
                select(sqlite_table)
            ).mappings().all()

            if not rows:

                results.append({
                    "table": table_name,
                    "status": "empty",
                    "rows": 0
                })

                continue

            # Check if PostgreSQL already contains data
            existing_count = postgres_conn.execute(
                select(
                    postgres_table
                ).limit(1)
            ).fetchone()

            if existing_count:

                results.append({
                    "table": table_name,
                    "status": "skipped",
                    "reason": "PostgreSQL table already contains data"
                })

                continue

            # ======================================
            # Insert rows
            # ======================================

            data = [
                dict(row)
                for row in rows
            ]

            postgres_conn.execute(
                postgres_table.insert(),
                data
            )

            results.append({
                "table": table_name,
                "status": "imported",
                "rows": len(data)
            })

        postgres_conn.commit()

        sqlite_conn.close()
        postgres_conn.close()

        return jsonify({
            "success": True,
            "message": "Database migration completed.",
            "results": results
        })

    except Exception as e:

        import traceback

        traceback.print_exc()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
@app.context_processor
def inject_settings():
    settings = AppSettings.query.first()
    if settings is None:
        settings = AppSettings()
        return dict(app_settings=settings)
with app.app_context():
    os.makedirs(
        app.instance_path,
        exist_ok=True
    )
    db.create_all()

return app
    
