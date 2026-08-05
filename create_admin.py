from getpass import getpass

from app import create_app
from app.extensions import db
from app.models.user import User


app = create_app()

with app.app_context():

    print("=" * 50)
    print("MGM - Create Admin User")
    print("=" * 50)

    # Check if an Admin already exists
    admin = User.query.filter_by(role="Admin").first()

    if admin:
        print("\nAn Admin account already exists!")
        print(f"Username : {admin.username}")
        exit()

    username = input("Username: ").strip()
    full_name = input("Full Name: ").strip()
    email = input("Email: ").strip()

    # Check username
    if User.query.filter_by(username=username).first():
        print("\nUsername already exists.")
        exit()

    # Check email
    if User.query.filter_by(email=email).first():
        print("\nEmail already exists.")
        exit()

    password = getpass("Password: ")
    confirm = getpass("Confirm Password: ")

    if password != confirm:
        print("\nPasswords do not match.")
        exit()

    user = User(
        username=username,
        full_name=full_name,
        email=email,
        role="Admin",
        is_active=True
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    print("\nAdmin created successfully.")