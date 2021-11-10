from monolith.classes.notify import NotifyModel
from monolith.classes.user import UserModel
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, jsonify
# from flask_mail import Mail, Message


from monolith.auth import current_user
from monolith.classes.message import MessageModel

home = Blueprint("home", __name__)


@home.route("/")
def index():

    if current_user.is_authenticated:
        return redirect(url_for('mailbox.mailbox_list_received'))

    return render_template("index_bs.html")


@home.route("/notification")
def notification():
    #pop-up notification
    notifies = NotifyModel.get_notify(current_user.get_id())
    return jsonify(notifications=notifies)
