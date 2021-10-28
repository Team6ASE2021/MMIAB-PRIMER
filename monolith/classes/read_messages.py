from typing import Optional
from monolith.database import db, User, Message
from datetime import datetime
import sqlalchemy


class MessModel:

    """
        Wrapper class  for all db operations involving messages
    """

    @staticmethod
    def get_message_by_id(id: int) -> Optional[Message]:
        mess = db.session.query(Message).filter(Message.id_message == id)
        mess = mess.first() #first row
        return mess

    @staticmethod
    def insert_db():
        admin_draft1 = Message()
        admin_draft1.body_message = 'admin draft 1'
        admin_draft1.id_sender = 1
        admin_draft1.id_receipent = 1
        db.session.add(admin_draft1)

        admin_draft2 = Message()
        admin_draft2.body_message = 'admin draft 2'
        admin_draft2.id_sender = 1
        admin_draft2.id_receipent = 1
        db.session.add(admin_draft2)

        admin_sent1 = Message()
        admin_sent1.body_message = 'admin send 1'
        admin_sent1.id_sender = 1
        admin_sent1.id_receipent = 1
        admin_sent1.date_of_send = datetime.now()
        admin_sent1.is_sended = True
        db.session.add(admin_sent1)

        admin_sent2 = Message()
        admin_sent2.body_message = 'admin send 2'
        admin_sent2.id_sender = 1
        admin_sent2.id_receipent = 1
        admin_sent2.date_of_send = datetime.now()
        admin_sent2.is_sended = True
        admin_sent2.is_received = True
        db.session.add(admin_sent2)

        admin_sent3 = Message()
        admin_sent3.body_message = 'admin send 3'
        admin_sent3.id_sender = 1
        admin_sent3.id_receipent = 1
        admin_sent3.date_of_send = datetime.now()
        admin_sent3.is_sended = True
        admin_sent3.is_received = True
        db.session.add(admin_sent3)

        new_user_draft1 = Message()
        new_user_draft1.body_message = 'new_user draft 1'
        new_user_draft1.id_sender = 1
        new_user_draft1.id_receipent = 1
        db.session.add(new_user_draft1)

        new_user_draft2 = Message()
        new_user_draft2.body_message = 'new_user draft 2'
        new_user_draft2.id_sender = 1
        new_user_draft2.id_receipent = 1
        db.session.add(new_user_draft2)

        new_user_draft3 = Message()
        new_user_draft3.body_message = 'new_user draft 3'
        new_user_draft3.id_sender = 1
        new_user_draft3.id_receipent = 1
        db.session.add(new_user_draft3)

        new_user_sent1 = Message()
        new_user_sent1.body_message = 'new_user send 1'
        new_user_sent1.id_sender = 1
        new_user_sent1.id_receipent = 1
        new_user_sent1.date_of_send = datetime.now()
        new_user_sent1.is_sended = True
        db.session.add(new_user_sent1)

        new_user_sent2 = Message()
        new_user_sent2.body_message = 'new_user send 2'
        new_user_sent2.id_sender = 1
        new_user_sent2.id_receipent = 1
        new_user_sent2.date_of_send = datetime.now()
        new_user_sent2.is_sended = True
        new_user_sent2.is_arrived = True
        db.session.add(new_user_sent2)

        new_user_sent3 = Message()
        new_user_sent3.body_message = 'new_user send 3'
        new_user_sent3.id_sender = 1
        new_user_sent3.id_receipent = 1
        new_user_sent3.date_of_send = datetime.now()
        new_user_sent3.is_sended = True
        new_user_sent3.is_arrived = True
        db.session.add(new_user_sent3)

        new_user_sent4 = Message()
        new_user_sent4.body_message = 'new_user send 4'
        new_user_sent4.id_sender = 1
        new_user_sent4.id_receipent = 1
        new_user_sent4.date_of_send = datetime.now()
        new_user_sent4.is_sended = True
        new_user_sent4.is_arrived = True
        db.session.add(new_user_sent4)

        db.session.commit()

    @staticmethod
    def remove_db():
        db.session.query(Message).delete()