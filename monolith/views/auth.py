from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask.helpers import flash
from flask.helpers import url_for
from flask_login import login_user
from flask_login import logout_user
from werkzeug.urls import url_parse

from monolith.classes.user import NotExistingUserError
from monolith.classes.user import UserModel
from monolith.forms import LoginForm

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]
        try:
            user = UserModel.get_user_info_by_email(email=email)
            if user.is_banned == True:
                flash("You are banned!")
                return redirect(url_for('auth.login'))
            elif user.authenticate(password):
                login_user(user)

                flash("Logged in!")
                next_page = request.args.get("next")
                if not next_page or url_parse(next_page).netloc != "":
                    next_page = url_for("home.index")

                return redirect(next_page)
            else:
                flash("Wrong password")
                return redirect(url_for("auth.login"))

        except NotExistingUserError:
            flash("No user with this email was found on this server")
            return redirect(url_for("auth.login"))

    return render_template("login_bs.html", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect("/")
