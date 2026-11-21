import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///" + os.path.join(INSTANCE_DIR, "mgms.db")
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ENVIRONMENT = os.getenv("FLASK_ENV", os.getenv("ENVIRONMENT", "development")).lower()

    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        if ENVIRONMENT in {"production", "prod", "railway"}:
            raise RuntimeError("SECRET_KEY must be configured in production.")
        SECRET_KEY = os.urandom(32)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = ENVIRONMENT in {"production", "prod", "railway"}
    PERMANENT_SESSION_LIFETIME = 28800
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
