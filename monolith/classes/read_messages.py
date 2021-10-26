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
    def test_insert_db():
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

        db.session.commit()

    @staticmethod
    def test_remove_db():
        db.session.query(Message).filter(Message.id_sender == 0).delete()
        db.session.commit()

        db.session.query(Message).filter(Message.id_sender == 1).delete()
        db.session.commit()