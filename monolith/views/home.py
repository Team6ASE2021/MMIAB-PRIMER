from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import url_for

from monolith.auth import current_user
from monolith.classes.notify import NotifyModel

# from flask_mail import Mail, Message

home = Blueprint("home", __name__)


@home.route("/")
def index():
    """
    simply returns a splash for not logged in users or its mailbox if the user is logged in
    """
    if current_user.is_authenticated:
        return redirect(url_for("mailbox.mailbox_list_received"))

    return render_template("index_bs.html")


@home.route("/notification")
def notification():
    # pop-up notification
    notifies = NotifyModel.get_notify(current_user.get_id())
    return jsonify(notifications=notifies)
