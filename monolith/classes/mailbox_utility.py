from monolith.database import db
from monolith.database import Message
from monolith.database import Recipient
from monolith.database import User


class MailboxUtility:
    @staticmethod
    def get_sended_message_by_id_user(id):
        mess = (
            db.session.query(Message)
            .filter(Message.id_sender == id, Message.is_sent == True)
            .all()
        )
        return mess

    @staticmethod
    def get_received_message_by_id_user(id):
        mess = (
            db.session.query(Message,User)
            .filter(Message.is_arrived == True)
            .filter(Message.recipients.any(Recipient.id_recipient == id))
        )
        if (
            db.session.query(User)
            .filter(User.id == id, User.content_filter == True)
            .count() 
            > 0
        ):
            mess = mess.filter(Message.to_filter == False)
        mess = mess.join(User, Message.id_sender == User.id).all()
        return mess

    @staticmethod
    def get_draft_message_by_id_user(id):
        mess = (
            db.session.query(Message)
            .filter(
                Message.id_sender == id, 
                Message.is_sent == False, 
                Message.is_arrived == False
            ).all()
        )
        return mess
