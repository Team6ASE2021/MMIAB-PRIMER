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
    def set_recipients(message: Message, recipients: List[int], replying:bool=False) -> None:
        _recipients = []
        for rcp in recipients:
            if rcp not in _recipients:
                _recipients.append(rcp)

        if replying:
            rep_msg = db.session.query(Message).filter(Message.id_message == message.reply_to).first()
            if rep_msg and rep_msg.id_sender not in _recipients:
                _recipients.insert(0, rep_msg.id_sender)

        message.recipients = [Recipient(id_recipient=user_id) for user_id in _recipients] 
        db.session.commit()




