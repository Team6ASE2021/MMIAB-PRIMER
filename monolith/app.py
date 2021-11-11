import datetime
import os

from flask import Flask
from flask_migrate import Migrate

from monolith.auth import login_manager
from monolith.constants import _UPLOAD_FOLDER
from monolith.database import db
from monolith.database import User
from monolith.views import blueprints

# from flask_mail import Mail


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config")
    app.config.from_pyfile("config.py")
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, _UPLOAD_FOLDER)
    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tests/mmiab.db"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/mmiab.db"

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)
    Migrate(app, db)
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


if __name__ == "__main__":
    app = create_app()
    app.run()
