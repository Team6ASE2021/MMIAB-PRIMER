import datetime
import string

import pytest

from monolith.classes.message import ContentFilter
from monolith.classes.message import MessageModel
from monolith.classes.message import NotExistingMessageError
from monolith.classes.user import UserModel
from monolith.database import db
from monolith.database import Message
from monolith.database import Recipient


@pytest.mark.usefixtures("clean_db_and_logout")
class TestMessage:
    def test_read_message(self):

        message = Message(
            id_sender=0,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)

        message1 = Message(
            id_sender=1,
            body_message="Ciao sono gino",
            date_of_send=datetime.datetime.strptime("07/01/2006", "%d/%m/%Y"),
        )
        db.session.add(message1)
        db.session.commit()

        message.recipients = [Recipient(id_recipient=1)]
        message1.recipients = [Recipient(id_recipient=1)]

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
        db.session.query(Message).filter(Message.id_sender == 1).delete()
        db.session.commit()

    def test_id_message_exists(self):
        db.session.query(Message).delete()
        db.session.commit()

        message = Message(
            id_message=1,
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
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

        db.session.query(Message).delete()
        db.session.commit()

    def test_id_message_not_exists(self):

        with pytest.raises(NotExistingMessageError):
            MessageModel.id_message_exists(1000)

    def test_send_message(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert message.is_sent == 0
        MessageModel.send_message(message.id_message)
        assert message.is_sent == 1

        db.session.query(Message).delete()
        db.session.commit()

    def test_arrived_message(self):
        message = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.datetime.now(),
            is_sent=True,
            is_arrived=False,
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]

        MessageModel.get_new_arrived_messages()
        assert message.is_arrived == True

        db.session.delete(message)
        db.session.commit()

    def test_delete_message_ok(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()
        _len = db.session.query(Message).count()

        MessageModel.delete_message(message.id_message)
        db.session.commit()
        nlen = db.session.query(Message).count()
        assert _len - nlen == 1

    def test_delete_read_message(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert MessageModel.delete_read_message(message.id_message, 2) == False
        assert message.recipients[0].read_deleted == False

        assert MessageModel.delete_read_message(message.id_message, 1) == False
        assert message.recipients[0].read_deleted == False

        message.recipients[0].has_opened = True
        db.session.commit()
        print(message.recipients[0].has_opened)
        assert MessageModel.delete_read_message(message.id_message, 1) == True
        assert message.recipients[0].read_deleted == True

        message.recipients = []
        db.session.delete(message)
        db.session.commit()

    def test_withdraw_message_not_exists(self):
        with pytest.raises(NotExistingMessageError):
            MessageModel.withdraw_message(1000)

    def test_withdraw_message_ok(self):
        message = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()
        id = db.session.query(Message).count()
        MessageModel.send_message(id)
        UserModel.update_points_to_user(1, 1)
        assert MessageModel.id_message_exists(id).is_sent
        assert UserModel.get_user_info_by_id(1).lottery_points == 1
        MessageModel.withdraw_message(id)
        assert not MessageModel.id_message_exists(id).is_sent
        assert UserModel.get_user_info_by_id(1).lottery_points == 0

        db.session.delete(message)

    def test_delete_message_not_exists(self):
        with pytest.raises(NotExistingMessageError):
            MessageModel.delete_message(1000)

    def test_user_cannot_read_arrived(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
            is_sent=True,
            is_arrived=True,
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert MessageModel.user_can_read(8, message) == False

        message.recipients = []
        db.session.delete(message)
        db.session.commit()

    def test_user_cannot_read_not_arrived(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
            is_sent=True,
            is_arrived=False,
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert MessageModel.user_can_read(1, message) == False

        message.recipients = []
        db.session.delete(message)
        db.session.commit()

    def test_user_can_read(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
            is_sent=True,
            is_arrived=True,
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert MessageModel.user_can_read(1, message) == True
        assert MessageModel.user_can_read(2, message) == True
        message.is_arrived = False
        db.session.commit()
        assert MessageModel.user_can_read(2, message) == True

        message.recipients = []
        db.session.delete(message)
        db.session.commit()

    def test_user_cannot_reply(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
            is_sent=True,
            is_arrived=False,
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert MessageModel.user_can_reply(1, message) == False
        message.is_arrived = True
        db.session.commit()
        assert MessageModel.user_can_reply(2, message) == False
        message.is_arrived = False
        db.session.commit()
        assert MessageModel.user_can_reply(2, message) == False

        message.recipients = []
        db.session.delete(message)
        db.session.commit()

    def test_user_can_reply(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
            is_sent=True,
            is_arrived=True,
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert MessageModel.user_can_reply(1, message) == True

        message.recipients = []
        db.session.delete(message)
        db.session.commit()

    def test_replying_info_no_reply(self):

        assert MessageModel.get_replying_info(None) == None
        assert MessageModel.get_replying_info(8) == None

        message = Message(
            id_sender=8,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
            is_sent=True,
            is_arrived=True,
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert MessageModel.get_replying_info(message.id_message) == None

        message.recipients = []
        db.session.delete(message)
        db.session.commit()

    def test_replying_info_ok(self):

        message = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y"),
            is_sent=True,
            is_arrived=True,
        )
        db.session.add(message)
        db.session.commit()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        info = MessageModel.get_replying_info(message.id_message)
        assert "message" in info
        assert info["message"].id_message == message.id_message
        assert "user" in info
        assert info["user"].id == 1

        message.recipients = []
        db.session.delete(message)
        db.session.commit()


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
