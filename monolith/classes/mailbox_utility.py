from typing import Optional
from monolith.database import db, User, Message
import datetime
import sqlalchemy

class MailboxUtility():

    @staticmethod
    def get_sended_message_by_id_user(id):
        mess = db.session.query(Message,User).filter(Message.id_sender == id,Message.is_sended == True)\
            .join(User,Message.id_receipent == User.id)
        return mess

    @staticmethod
    def get_received_message_by_id_user(id):
        mess = db.session.query(Message,User).filter(Message.id_receipent == id, Message.is_arrived == True)\
            .join(User,Message.id_sender== User.id)
        return mess

    @staticmethod
    def get_draft_message_by_id_user(id):
        mess = db.session.query(Message,User).filter(Message.id_sender == id, Message.is_sended == False, Message.is_arrived == False)\
            .join(User,Message.id_receipent == User.id)
        return mess