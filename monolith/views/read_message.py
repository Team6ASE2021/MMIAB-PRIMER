from flask import Blueprint, redirect, render_template, request, abort
from flask_login.utils import login_required
from monolith.database import Message, User, db
from monolith.auth import current_user
from monolith.classes.message import MessageModel, NotExistingMessageError
from monolith.classes.user import UserModel, NotExistingUserError
from monolith.classes.recipient import RecipientModel

read_message = Blueprint('read_message', __name__)


@read_message.route('/read_message/<int:id>', methods=['GET'])
@login_required
def read_messages(id):
    # check if the user is authenticated
    mess_text = sender_email = date_receipt = None
    user_allowed = True

    try:
        mess = MessageModel.id_message_exists(id)
    except NotExistingMessageError:
        abort(404, description="Message not found")

    sender_id = mess.id_sender
    mess_text = mess.body_message
    date_receipt = mess.date_of_send

    # some controls to check if user is allowed to read the message or not
    if (mess.is_arrived == True):
        if current_user.id not in RecipientModel.get_recipients(mess) and current_user.id != mess.id_sender:
            user_allowed = False
    elif (current_user.get_id() != mess.id_sender):
        user_allowed = False

    sender_email = ""
    try:
        sender = UserModel.get_user_info_by_id(sender_id)
        sender_email = sender.email
    except NotExistingUserError:
        sender_email = "Anonymous"

    return render_template("read_select_message.html", user_allowed=user_allowed, mess_text=mess_text, sender=sender_email, date_receipt=date_receipt)
