from typing import Optional
from monolith.database import db, User, Message
import datetime
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
        message = Message(
        id_receipent = 1, \
        id_sender = 0, \
        body_message = "Ciao", \
        date_of_send = datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"))
        db.session.add(message)

        message1 = Message(
        id_receipent = 1, \
        id_sender = 1, \
        body_message = "Ciao sono gino", \
        date_of_send = datetime.datetime.strptime("07/01/2006", "%d/%m/%Y"))
        db.session.add(message1)

        message2 = Message(
        id_receipent = 1, \
        is_arrived = 1, \
        id_sender = None, \
        body_message = "mess anonimo", \
        date_of_send = datetime.datetime.strptime("07/01/2006", "%d/%m/%Y"))
        db.session.add(message2)

        db.session.commit()

        message3 = Message(
        id_receipent = 3, \
        is_arrived = 1, \
        id_sender = 3, \
        body_message = "test3", \
        date_of_send = datetime.datetime.strptime("07/01/2006", "%d/%m/%Y"))
        db.session.add(message3)

        db.session.commit()

        message4 = Message(
        id_receipent = 3, \
        is_arrived = 0, \
        id_sender = 3, \
        body_message = "test4", \
        date_of_send = datetime.datetime.strptime("07/01/2006", "%d/%m/%Y"))
        db.session.add(message4)

        db.session.commit()

    @staticmethod
    def remove_db():
        db.session.query(Message).filter(Message.id_sender == 0).delete()
        db.session.commit()

        db.session.query(Message).filter(Message.id_sender == 1).delete()
        db.session.commit()

        db.session.query(Message).filter(Message.body_message == "mess anonimo").delete()
        db.session.commit()

        db.session.query(Message).filter(Message.body_message == "test3").delete()
        db.session.commit()

        db.session.query(Message).filter(Message.body_message == "test4").delete()
        db.session.commit()