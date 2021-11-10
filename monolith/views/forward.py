from flask import abort
from flask import Blueprint
from flask import redirect
from flask_login.utils import login_required

from monolith.auth import current_user
from monolith.classes.message import MessageModel
from monolith.classes.message import NotExistingMessageError
from monolith.database import db
from monolith.database import Message

forward = Blueprint("forward", __name__)


@forward.route("/forwarding/<int:id>", methods=["GET"])
@login_required
def forward_messages(id):
    """
    Setup the draft form for forwarding a message
    :param id:  id of message to be forwarded
    :return: draft form template
    """
    try:
        mess = MessageModel.id_message_exists(id)

        # insert the message in the db
        new_message = Message()
        new_message.body_message = mess.body_message
        new_message.id_sender = current_user.get_id()
        db.session.add(new_message)
        db.session.commit()

        id_forwarded_mess = new_message.id_message

        return redirect("/draft/edit/" + str(id_forwarded_mess))
    except NotExistingMessageError:
        abort(404, "Message not foud!")
