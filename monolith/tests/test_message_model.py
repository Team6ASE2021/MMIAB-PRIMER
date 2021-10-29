import sqlalchemy
import datetime
from monolith.forms import UserForm
from monolith.database import db, Message
from monolith.classes.message import MessageModel, NotExistingMessageError
import pytest

class TestMessage:

    def test_id_message_exists(self,test_msg,session):
       
        session.add(test_msg)
        session.commit()

        message_out = MessageModel.id_message_exists(test_msg.id_message)
        assert message_out.id_message == 1
        assert message_out.body_message == "Ciao"
        assert message_out.date_of_send == datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        session.delete(test_msg)
        session.commit()

    def test_id_message_not_exists(self):

        with pytest.raises(NotExistingMessageError):
            message = MessageModel.id_message_exists(1000)
        

    def test_send_message(self,test_msg,session):
      
        session.add(test_msg)
        session.commit()

        assert test_msg.is_sended == 0
        MessageModel.send_message(test_msg.id_message)
        assert test_msg.is_sended == 1
        session.delete(test_msg)
        session.commit() 
        