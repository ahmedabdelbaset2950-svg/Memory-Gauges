from app.models.user import User


def authenticate_user(username, password):
    """
    Authenticate using username or email.
    """

    user = User.query.filter(
        (User.username == username) |
        (User.email == username)
    ).first()

    if user is None:
        return None

    if not user.check_password(password):
        return None

    if not user.is_active:
        return None

    return user