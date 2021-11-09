from monolith.classes.notify import NotifyModel
from monolith.classes.user import UserModel
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, jsonify
# from flask_mail import Mail, Message


from monolith.auth import current_user
from monolith.classes.message import MessageModel

home = Blueprint("home", __name__)


@home.route("/")
def index():

    if current_user is not None and hasattr(current_user, "id"):
        welcome = "Logged In!"

    else:
        welcome = None

    return render_template("index.html", welcome=welcome)

@home.route("/notification")
def notification():
    #pop-up notification
    notifies = NotifyModel.get_notify(current_user.get_id())
    return jsonify({"notify_list" : notifies})