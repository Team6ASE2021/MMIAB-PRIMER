import sqlalchemy
import datetime
from monolith.forms import UserForm
from monolith.database import db, Message
from monolith.classes.message import MessageModel, NotExistingMessageError
from monolith.classes.user import UserModel
import pytest

class TestMessage:

    def test_id_message_exists(self):
        message = Message(id_message = 1,\
                          id_receipent = 1, \
                          id_sender = 2, \
                          body_message = "Ciao", \
                          date_of_send = datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"))
        db.session.add(message)
        db.session.commit()

        message_out = MessageModel.id_message_exists(message.id_message)
        assert message_out.id_message == 1
        assert message_out.body_message == "Ciao"
        assert message_out.date_of_send == datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")

    def test_id_message_not_exists(self):

        with pytest.raises(NotExistingMessageError):
            message = MessageModel.id_message_exists(1000)
        

    def test_send_message(self):
        message = Message(id_receipent = 1, \
                          id_sender = 2, \
                          body_message = "Ciao", \
                          date_of_send = datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"))
        db.session.add(message)
        db.session.commit()

        assert message.is_sended == 0
        MessageModel.send_message(message.id_message)
        assert message.is_sended == 1

    def test_arrived_message(self):
        message = Message(id_receipent = 1, \
                          id_sender = 1, \
                          body_message = "Ciao", \
                          date_of_send = datetime.datetime.now(), \
                          is_sended = True, \
                          is_arrived = False)
        
        db.session.add(message)

        MessageModel.arrived_message()
        assert message.is_arrived == True

        db.session.delete(message)
        db.session.commit()

    def test_get_notify(self):
        message = Message(id_receipent = 1, \
                          id_sender = 1, \
                          body_message = "Ciao", \
                          date_of_send = datetime.datetime.now(), \
                          is_sended = True, \
                          is_arrived = True, \
                          is_notified = False)
        
        db.session.add(message)

        MessageModel.get_notify(UserModel.get_user_info_by_id(message.id_receipent))
        assert message.is_notified == True

        db.session.delete(message)
        db.session.commit()
