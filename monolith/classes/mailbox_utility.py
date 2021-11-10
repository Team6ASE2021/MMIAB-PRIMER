from sqlalchemy import and_

from monolith.database import db
from monolith.database import Message
from monolith.database import Recipient
from monolith.database import User


class MailboxUtility:
    """
    Utility class to handle mailbox db calls
    """

    @staticmethod
    def get_sended_message_by_id_user(id):
        """
        Returns the list of sent messages by a specific user.
        """
        mess = (
            db.session.query(Message)
            .filter(Message.id_sender == id, Message.is_sent == True)
            .all()
        )
        return mess

    @staticmethod
    def get_received_message_by_id_user(id):
        """
        Returns the list of received messages by a specific user,
        filtering out those which contain unsafe words if the user
        has this option enabled.
        """
        mess = (
            db.session.query(Message, User)
            .filter(Message.is_arrived == True)
            .filter(
                Message.recipients.any(
                    and_(Recipient.id_recipient == id, Recipient.read_deleted == False)
                )
            )
        )
        if (
            db.session.query(User)
            .filter(User.id == id, User.content_filter == True)
            .count()
            > 0
        ):
            mess = mess.filter(Message.to_filter == False)
        mess = mess.join(User, Message.id_sender == User.id).all()
        opened_dict = {
            m.Message.id_message: next(
                (
                    rcp.has_opened
                    for rcp in m.Message.recipients
                    if rcp.id_recipient == id
                ),
                True,
            )
            for m in mess
        }

        return mess, opened_dict

    @staticmethod
    def get_draft_message_by_id_user(id):
        """
        Returns the list of drafts created by a specific user.
        """
        mess = (
            db.session.query(Message)
            .filter(
                Message.id_sender == id,
                Message.is_sent == False,
                Message.is_arrived == False,
            )
            .all()
        )
        return mess
