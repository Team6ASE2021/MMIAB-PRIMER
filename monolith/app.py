import datetime
import os

from flask import Flask
# from flask_mail import Mail

from monolith.auth import login_manager
from monolith.constants import _ALLOWED_EXTENSIONS
from monolith.constants import _MAX_CONTENT_LENGTH
from monolith.constants import _UPLOAD_FOLDER
from monolith.database import db
from monolith.database import User
from monolith.views import blueprints


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config["WTF_CSRF_SECRET_KEY"] = "A SECRET KEY"
    app.config["SECRET_KEY"] = "ANOTHER ONE"
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, _UPLOAD_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = _MAX_CONTENT_LENGTH
    app.config["UPLOAD_EXTENSIONS"] = _ALLOWED_EXTENSIONS
    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tests/mmiab.db"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../mmiab.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
    app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        q = db.session.query(User).filter(User.email == "example@example.com")
        user = q.first()
        if user is None:
            example = User()
            example.firstname = "Admin"
            example.lastname = "Admin"
            example.email = "example@example.com"
            example.dateofbirth = datetime.datetime(2020, 10, 5)
            example.is_admin = True
            example.set_password("admin")
            db.session.add(example)
            db.session.commit()

    return app


app = create_app()
# mail = Mail(app)

if __name__ == "__main__":
    app.run()
