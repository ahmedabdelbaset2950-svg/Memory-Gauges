import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(INSTANCE_DIR, "mgms.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False