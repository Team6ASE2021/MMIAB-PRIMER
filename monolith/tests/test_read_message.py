import sqlalchemy
import datetime
from monolith.forms import MessageForm, UserForm
from monolith.database import db, User, Message
from monolith.classes.user import UserModel
from monolith.classes.read_messages import MessModel
import pytest

class TestReadMessages:

    '''
message = Message(id_message = 1,\

id_receipent = 1, \

id_sender = 2, \

body_message = "Ciao", \

date_of_send = datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"))

db.session.add(message)
db.session.commit()
'''

    def test_read_message(self):
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

        conto = db.session.query(Message).count()
        assert conto == 2

        mess = MessModel.get_message_by_id(1)
        assert mess is not None
        assert mess.body_message == "Ciao"

        mess2 = MessModel.get_message_by_id(2)
        assert mess2 is not None
        assert mess2.id_sender == 1

        db.session.query(Message).filter(Message.id_sender == 0).delete()
        db.session.commit()

        db.session.query(Message).filter(Message.id_sender == 1).delete()
        db.session.commit()

