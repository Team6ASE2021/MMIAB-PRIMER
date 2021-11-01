from flask import abort
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request

from monolith.auth import current_user
from monolith.classes.mailbox_utility import MailboxUtility
from monolith.classes.user import UserModel
from monolith.database import db
from monolith.database import Message
from monolith.database import User

mailbox = Blueprint("mailbox", __name__)


@mailbox.route("/message/list/sent", methods=["GET"])
# get message id to retrive message from the db table
def mailbox_list_sent():

    message_list = []
    if current_user.is_authenticated:
        message_list = MailboxUtility.get_sended_message_by_id_user(
            current_user.get_id()
        )

    return render_template("mailbox.html", message_list=message_list, list_type="sent")


@mailbox.route("/message/list/received", methods=["GET"])
def mailbox_list_received():

    message_list = []
    if current_user.is_authenticated:
        message_list = MailboxUtility.get_received_message_by_id_user(
            current_user.get_id()
        )

    return render_template(
        "mailbox.html", message_list=message_list, list_type="received"
    )


@mailbox.route("/message/list/draft", methods=["GET"])
def mailbox_list_draft():

    message_list = []
    if current_user.is_authenticated:
        message_list = MailboxUtility.get_draft_message_by_id_user(
            current_user.get_id()
        )

    return render_template("mailbox.html", message_list=message_list, list_type="draft")
