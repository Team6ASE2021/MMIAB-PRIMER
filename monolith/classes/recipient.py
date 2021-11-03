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
    def set_recipients(message: Message, recipients: List[int]) -> None:
        message.recipients = [Recipient(id_recipient=user_id) for user_id in recipients] 
        db.session.commit()

    """
    @staticmethod
    def delete_recipients(message: Message) -> None:
        message.recipients = []
        RecipientModel._clean_orphans()
    """





