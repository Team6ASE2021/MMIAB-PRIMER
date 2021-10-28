from typing import Optional
from monolith.database import db, User, Message
import datetime
import sqlalchemy

class MailboxUtility():

    @staticmethod
    def get_sended_message_by_id_user(id):
        mess = db.session.query(Message).join(User,User.id == Message.id_sender,User.id == Message.id_receipent) \
            .filter(Message.id_sender == id, Message.is_sended == True)
        return mess

    @staticmethod
    def get_received_message_by_id_user(id):
        mess = db.session.query(Message).filter(Message.id_receipent == id, Message.is_arrived == True)
        return mess

    @staticmethod
    def get_draft_message_by_id_user(id):
        mess = db.session.query(Message).filter(Message.id_sender == id, Message.is_sended == False, Message.is_arrived == False)
        return mess