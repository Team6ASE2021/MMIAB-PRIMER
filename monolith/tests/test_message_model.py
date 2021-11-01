import datetime
import string

import pytest

from monolith.classes.message import ContentFilter
from monolith.classes.message import MessageModel
from monolith.classes.message import NotExistingMessageError
from monolith.classes.user import UserModel
from monolith.database import db
from monolith.database import Message


@pytest.mark.usefixtures("clean_db_and_logout")
class TestMessage:
    def test_read_message(self):

        message = Message(
            id_receipent=1,
            id_sender=0,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)

        message1 = Message(
            id_receipent=1,
            id_sender=1,
            body_message="Ciao sono gino",
            date_of_send=datetime.datetime.strptime("07/01/2006", "%d/%m/%Y"),
        )
        db.session.add(message1)

        db.session.commit()

        conto = db.session.query(Message).count()
        assert conto == 2

        try:
            mess = MessageModel.id_message_exists(1)
        except NotExistingMessageError:
            assert False  # should not happen
        assert mess is not None
        assert mess.body_message == "Ciao"

        try:
            mess2 = MessageModel.id_message_exists(2)
        except NotExistingMessageError:
            assert False  # should not happen
        assert mess2 is not None
        assert mess2.id_sender == 1

        db.session.query(Message).filter(Message.id_sender == 0).delete()
        db.session.commit()

        db.session.query(Message).filter(Message.id_sender == 1).delete()
        db.session.commit()

    def test_id_message_exists(self):
        db.session.query(Message).delete()
        db.session.commit()

        message = Message(
            id_message=1,
            id_receipent=1,
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()

        try:
            message_out = MessageModel.id_message_exists(message.id_message)
        except NotExistingMessageError:
            assert False  # should not happen
        assert message_out.id_message == 1
        assert message_out.body_message == "Ciao"
        assert message_out.date_of_send == datetime.datetime.strptime(
            "01/01/2000", "%d/%m/%Y"
        )

    def test_id_message_not_exists(self):

        with pytest.raises(NotExistingMessageError):
            message = MessageModel.id_message_exists(1000)

    def test_send_message(self):
        message = Message(
            id_receipent=1,
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()

        assert message.is_sended == 0
        MessageModel.send_message(message.id_message)
        assert message.is_sended == 1

    def test_arrived_message(self):
        message = Message(
            id_receipent=1,
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.datetime.now(),
            is_sended=True,
            is_arrived=False,
        )

        db.session.add(message)

        MessageModel.arrived_message()
        assert message.is_arrived == True

        db.session.delete(message)
        db.session.commit()

    def test_get_notify(self):
        message = Message(
            id_receipent=1,
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.datetime.now(),
            is_sended=True,
            is_arrived=True,
            is_notified=False,
        )

        db.session.add(message)

        MessageModel.get_notify(UserModel.get_user_info_by_id(message.id_receipent))
        assert message.is_notified == True

        db.session.delete(message)
        db.session.commit()

    def test_delete_message_ok(self):
        message = Message(
            id_receipent=1,
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()
        len = db.session.query(Message).count()
        MessageModel.delete_message(message.id_message)
        nlen = db.session.query(Message).count()
        assert len - nlen == 1

    def test_delete_message_not_exists(self):
        with pytest.raises(NotExistingMessageError):
            MessageModel.delete_message(1000)


class TestMessageContentFilter:
    def test_content_filter_unsafe(self):
        _uw = ContentFilter.unsafe_words()
        for d in string.punctuation:
            message = d.join([_uw[0], _uw[-1]])
            assert ContentFilter.filter_content(message) == True
            message = d.join([_uw[0], _uw[-1], _uw[len(_uw) // 2]])
            assert ContentFilter.filter_content(message) == True

        message = _uw[0]
        assert ContentFilter.filter_content(message) == True

        message = "".join([_uw[0], _uw[-1], _uw[len(_uw) // 2]])
        assert ContentFilter.filter_content(message) == False

    def test_content_filter_safe(self):
        message = "good deeds"
        assert ContentFilter.filter_content(message) == False
