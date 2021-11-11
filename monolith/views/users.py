import os
from http import HTTPStatus
from typing import Optional
from typing import Text
from uuid import uuid4

from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask.globals import current_app
from flask.helpers import flash
from flask.helpers import url_for
from flask.wrappers import Response
from flask_login import current_user
from flask_login.utils import login_required
from werkzeug.utils import secure_filename

from monolith.classes.report import ReportModel
from monolith.classes.user import BlockingCurrentUserError
from monolith.classes.user import EmailAlreadyExistingError
from monolith.classes.user import NotExistingUserError
from monolith.classes.user import UserBlacklist
from monolith.classes.user import UserModel
from monolith.classes.user import WrongPasswordError
from monolith.database import User
from monolith.forms import EditProfileForm
from monolith.forms import UserForm

users = Blueprint("users", __name__)


@users.route("/create_user", methods=["POST", "GET"])
def create_user() -> Text:
    """
    View handling user creation
    """
    form = UserForm()

    if request.method == "POST":
        if form.validate_on_submit():
            if UserModel.user_exists(email=form.email.data):
                flash("An user with this email already exists")
            else:
                new_user = User()
                form.populate_obj(new_user)
                if form.profile_picture.data:
                    # store the image with a secured unique filename, storing relative path of the file
                    # in the database
                    file = form.profile_picture.data
                    name = file.filename
                    name = str(uuid4()) + secure_filename(name)

                    path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
                    new_user.set_pfp_path(name)
                    file.save(path)

                UserModel.create_user(new_user, form.password.data)
                return redirect("/login")

    return render_template("create_user_bs.html", form=form)


@users.route("/user/profile", methods=["POST", "GET"])
@login_required
def profile_info() -> Text:
    """
    renders the current user profile page
    """
    return redirect(url_for("users.user_info", id=current_user.id))


@users.route("/user/profile/edit", methods=["POST", "GET"])
@login_required
def edit_profile():
    """
    route handling editing of user info
    """
    form = EditProfileForm()

    if request.method == "POST":
        if form.validate_on_submit():
            # this filters non empty fields in a concise way
            form_data = {
                i: form.data[i] for i in form.data if i not in ["csrf_token", "submit"]
            }
            new_data = {k: v for k, v in form_data.items() if v is not None and v != ""}

            try:
                UserModel.update_user(current_user.id, new_data)
                return redirect(url_for("users.profile_info"))
            except (
                NotExistingUserError,
                WrongPasswordError,
                EmailAlreadyExistingError,
            ) as e:
                flash(e)

    user_data = UserModel.get_user_dict_by_id(current_user.id)
    return render_template("create_user_bs.html", form=form, user_data=user_data)


@users.route("/users/<int:id>", methods=["GET"])
@login_required
def user_info(id: int) -> Text:
    """
    Displays user_info identified by the id
    :param id: id of user to display
    :return: template showing user info
    """
    try:
        user = UserModel.get_user_info_by_id(id)
        return render_template(
            "user_info_bs.html",
            user=user,
            blocked=UserBlacklist.is_user_blocked(current_user.id, id),
            reported=ReportModel.is_user_reported(current_user.id, id),
        )

    except NotExistingUserError:
        abort(HTTPStatus.NOT_FOUND)


@users.route("/user_list", methods=["GET"])
@login_required
def user_list() -> Optional[Text]:
    _q = request.args.get("q", None)
    user_list = list(
        filter(
            lambda u: u.id != current_user.id,
            UserModel.search_user_by_keyword(current_user.id, _q),
        )
    )
    return render_template("user_list_bs.html", list=user_list)


@users.route("/user/delete", methods=["GET"])
@login_required
def delete_user() -> Response:
    UserModel.delete_user(current_user.get_id())
    flash("We're sad to see you go!")
    return redirect("/logout")


@users.route("/user/content_filter", methods=["GET"])
@login_required
def set_content_filter():
    UserModel.toggle_content_filter(current_user.id)
    return redirect("/users/" + str(current_user.id))


@users.route("/user/report/<int:id>", methods=["GET"])
@login_required
def report(id):
    """
    Route to report the user identified by id
    :param id: id of user reported

    """
    res = ReportModel.add_report(id, current_user.id)

    if res:
        flash(f"You have reported the user: {id}")
    else:
        flash("You have already reported this user")

    return redirect(url_for("users.user_info", id=id))


"""
Routes handling blacklist operations
"""


@users.route("/user/blacklist", methods=["GET"])
@login_required
def blacklist():
    _q = request.args.get("q", None)
    user_list = list(
        filter(
            lambda u: u.id != current_user.id,
            UserModel.search_blacklist_by_keyword(current_user.id, _q),
        )
    )
    return render_template("user_list_bs.html", list=user_list, blacklist=True)


@users.route("/user/blacklist/add/<int:id>", methods=["GET"])
@login_required
def blacklist_add(id: int):
    try:
        UserBlacklist.add_user_to_blacklist(current_user.id, id)
    except NotExistingUserError as e:
        abort(HTTPStatus.NOT_FOUND, description=str(e))
    except BlockingCurrentUserError as e:
        abort(HTTPStatus.FORBIDDEN, description=str(e))

    return redirect("/user/blacklist")


@users.route("/user/blacklist/remove/<int:id>", methods=["GET"])
@login_required
def blacklist_remove(id: int):
    try:
        UserBlacklist.remove_user_from_blacklist(current_user.id, id)
    except NotExistingUserError as e:
        abort(HTTPStatus.NOT_FOUND, description=str(e))

    return redirect("/user/blacklist")
