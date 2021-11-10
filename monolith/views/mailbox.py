from flask import Blueprint
from flask import render_template
from flask_login.utils import login_required

from monolith.auth import current_user
from monolith.classes.mailbox_utility import MailboxUtility

mailbox = Blueprint("mailbox", __name__)


@mailbox.route("/message/list/sent", methods=["GET"])
@login_required
def mailbox_list_sent():

    message_list = []
    if current_user.is_authenticated:
        message_list = MailboxUtility.get_sended_message_by_id_user(
            current_user.get_id()
        )

    return render_template(
        "mailbox_bs.html",
        message_list=message_list,
        list_type="sent",
        withdraw=current_user.lottery_points > 0,
    )


@mailbox.route("/message/list/received", methods=["GET"])
@login_required
def mailbox_list_received():

    message_list = []
    opened_dict = {}
    if current_user.is_authenticated:
        message_list, opened_dict = MailboxUtility.get_received_message_by_id_user(
            current_user.get_id()
        )

    return render_template(
        "mailbox_bs.html",
        message_list=message_list,
        opened_dict=opened_dict,
        list_type="received",
    )


@mailbox.route("/message/list/draft", methods=["GET"])
@login_required
def mailbox_list_draft():

    message_list = []
    if current_user.is_authenticated:
        message_list = MailboxUtility.get_draft_message_by_id_user(
            current_user.get_id()
        )

    return render_template(
        "mailbox_bs.html", message_list=message_list, list_type="draft"
    )
