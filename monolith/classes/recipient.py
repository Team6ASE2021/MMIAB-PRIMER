from typing import List

from monolith.database import db, Recipient, Message, User

class RecipientModel:
    """
        Wrapper class for all db operations involving recipients
    """

    @staticmethod
    def get_recipients(message: Message) -> List[int]:
        return [recipient.id_recipient for recipient in message.recipients]

    @staticmethod
    def add_recipients(message: Message, recipients: List[int]) -> None:
        db.session.flush()
        for user_id in recipients:
            message.recipients.append(Recipient(id_recipient=user_id))
        db.session.commit()

    @staticmethod
    def update_recipients(message: Message, recipients: List[int]) -> None:
        db.session.query(Recipient).filter(Recipient.id_message == message.id_message).delete()
        db.session.commit()
        message.recipients = []
        RecipientModel.add_recipients(message, recipients)

    @staticmethod
    def delete_recipients(message: Message) -> None:
        db.session.query(Recipient).filter(Recipient.id_message == message.id_message).delete()
        db.session.commit()
        message.recipients = []
        db.session.commit()







