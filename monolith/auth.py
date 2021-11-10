import functools

from flask_login import current_user
from flask_login import LoginManager

from monolith.database import User

# setup for the login required decorator redirects
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "you must be logged in to view this page"
login_manager.login_message_category = "warning"


def admin_required(func):  # pragma: no cover
    """
    this is not used right now, kept for future extensions that considers
    admin actions
    """

    @functools.wraps(func)
    def _admin_required(*args, **kw):
        admin = current_user.is_authenticated and current_user.is_admin
        if not admin:
            return login_manager.unauthorized()
        return func(*args, **kw)

    return _admin_required


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        user._authenticated = True
    return user
