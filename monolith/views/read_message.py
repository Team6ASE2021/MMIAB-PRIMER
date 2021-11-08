from flask import abort
from flask import Blueprint
from flask import render_template
from flask_login.utils import login_required

from monolith.auth import current_user
from monolith.classes.message import MessageModel
from monolith.classes.message import NotExistingMessageError
from monolith.classes.user import NotExistingUserError
from monolith.classes.user import UserModel

from http import HTTPStatus

read_message = Blueprint("read_message", __name__)


@read_message.route("/read_message/<int:id>", methods=["GET"])
@login_required
def read_messages(id):

    try:
        mess = MessageModel.id_message_exists(id)
    except NotExistingMessageError:
        abort(HTTPStatus.NOT_FOUND, description="Message not found")

    replying_info = MessageModel.get_replying_info(mess.reply_to)

    # some controls to check if user is allowed to read the message or not
    if not MessageModel.user_can_read(current_user.id, mess):
        abort(HTTPStatus.UNAUTHORIZED, description="You are not allowed to read this message")

    try:
        sender = UserModel.get_user_info_by_id(mess.id_sender)
    except NotExistingUserError:
        sender = None

    return render_template(
        "read_message_bs.html",
        message=mess,
        sender=sender,
        replying_info=replying_info,
    )
