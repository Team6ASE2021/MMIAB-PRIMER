import sqlalchemy
import datetime
from monolith.forms import UserForm
from monolith.database import db, Message
from monolith.classes.message import MessageModel, NotExistingMessageError, unsafe_words
import pytest

@pytest.mark.usefixtures('clean_db_and_logout')
class TestMessage:

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

        try:
            mess = MessageModel.id_message_exists(1)
        except NotExistingMessageError:
            assert False # should not happen
        assert mess is not None
        assert mess.body_message == "Ciao"

        try:
            mess2 = MessageModel.id_message_exists(2)
        except NotExistingMessageError:
            assert False # should not happen
        assert mess2 is not None
        assert mess2.id_sender == 1

        db.session.query(Message).filter(Message.id_sender == 0).delete()
        db.session.commit()

        db.session.query(Message).filter(Message.id_sender == 1).delete()
        db.session.commit()

    def test_id_message_exists(self):
        db.session.query(Message).delete()
        db.session.commit()

        message = Message(id_message = 1,\
                          id_receipent = 1, \
                          id_sender = 2, \
                          body_message = "Ciao", \
                          date_of_send = datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"))
        db.session.add(message)
        db.session.commit()

        try:
            message_out = MessageModel.id_message_exists(message.id_message)
        except NotExistingMessageError:
            assert False # should not happen
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

class TestMessageContentFilter:

    def test_content_filter_unsafe(self):
        message = ' '.join([unsafe_words[0], unsafe_words[-1], unsafe_words[len(unsafe_words)/2]])
        assert MessageModel.filter_content(message) == True

    def test_content_filter_safe(self):
        message = 'good deeds'
        assert MessageModel.filter_content(message) == False



