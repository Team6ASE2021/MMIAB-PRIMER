from datetime import datetime

import pytest

from monolith.classes.recipient import RecipientModel
from monolith.classes.user import UserModel
from monolith.database import db
from monolith.database import Message
from monolith.database import Recipient
from monolith.database import User


@pytest.fixture(scope="class")
def recipient_setup():
    new_user = {
        "email": "example1@example1.com",
        "firstname": "jack",
        "lastname": "black",
        "password": "admin1",
        "dateofbirth": "01/01/1990",
    }

    UserModel.create_user(
        User(
            email=new_user["email"],
            firstname=new_user["firstname"],
            lastname=new_user["lastname"],
            dateofbirth=datetime.strptime(new_user["dateofbirth"], "%d/%m/%Y"),
        ),
        password=new_user["password"],
    )


@pytest.mark.usefixtures("clean_db_and_logout", "recipient_setup")
class TestRecipientModel:
    def test_recipient_change_and_delete(self):
        new_user = {
            "email": "example1@example1.com",
            "firstname": "jack",
            "lastname": "black",
            "password": "admin1",
            "dateofbirth": "01/01/1990",
        }

        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.flush()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 1
        assert (
            db.session.query(Message).first().recipients[0].id_recipient
            == db.session.query(Recipient).first().id_recipient
        )

        message.recipients = [Recipient(id_recipient=2)]
        db.session.commit()
        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 1
        assert (
            db.session.query(Message).first().recipients[0].id_recipient
            == db.session.query(Recipient).first().id_recipient
        )
        assert db.session.query(Recipient).first().id_recipient == 2

        message.recipients = []
        db.session.query(Message).delete()
        db.session.commit()
        assert db.session.query(Recipient).count() == 0
        assert db.session.query(Message).count() == 0

    def test_recipient_set(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.flush()
        RecipientModel.set_recipients(message, [1, 2])

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 2
        assert (
            db.session.query(Message).first().recipients[0].id_recipient
            == db.session.query(Recipient).first().id_recipient
        )
        assert (
            db.session.query(Message).first().recipients[1].id_recipient
            == db.session.query(Recipient).all()[1].id_recipient
        )

        RecipientModel.set_recipients(message, [2, 2])

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 1
        assert (
            db.session.query(Message).first().recipients[0].id_recipient
            == db.session.query(Recipient).first().id_recipient
        )

        RecipientModel.set_recipients(message, [2])

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 1
        assert (
            db.session.query(Message).first().recipients[0].id_recipient
            == db.session.query(Recipient).first().id_recipient
        )

        RecipientModel.set_recipients(message, [])

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 0

        db.session.query(Message).delete()
        db.session.commit()
        assert db.session.query(Message).count() == 0

    def test_recipient_set_replying(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2000", "%d/%m/%Y"),
            is_sent=True,
            is_arrived=True,
        )
        db.session.add(message)
        db.session.flush()
        message2 = Message(
            id_sender=1,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2000", "%d/%m/%Y"),
            reply_to=1,
        )
        db.session.add(message2)
        db.session.flush()
        RecipientModel.set_recipients(message, [1])
        RecipientModel.set_recipients(message2, [2], replying=True)

        assert message.recipients[0].id_recipient == 1
        assert message2.recipients[0].id_recipient == 2

        RecipientModel.set_recipients(message2, [1], replying=True)

        assert message2.recipients[0].id_recipient == 2
        assert message2.recipients[1].id_recipient == 1

        RecipientModel.set_recipients(message, [])
        RecipientModel.set_recipients(message2, [])
        db.session.query(Message).delete()
        db.session.commit()

    def test_recipient_get(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.flush()
        message.recipients = [Recipient(id_recipient=1), Recipient(id_recipient=2)]
        db.session.commit()

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 2
        assert RecipientModel.get_recipients(message) == [1, 2]

        message.recipients = [Recipient(id_recipient=2)]
        db.session.commit()

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 1
        assert RecipientModel.get_recipients(message) == [2]

        message.recipients = []
        db.session.commit()

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 0
        assert RecipientModel.get_recipients(message) == []

        db.session.query(Message).delete()
        db.session.commit()
        assert db.session.query(Message).count() == 0

    def test_recipient_has_opened_fail(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.commit()

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 0

        assert RecipientModel.has_opened(None, 1) == False
        assert RecipientModel.has_opened(message, 1) == False

        RecipientModel.set_recipients(message, [])
        db.session.query(Message).delete()
        db.session.commit()
        assert db.session.query(Message).count() == 0

    def test_recipient_has_opened_ok(self):
        message = Message(
            id_sender=2,
            body_message="Ciao",
            date_of_send=datetime.strptime("01/01/2000", "%d/%m/%Y"),
        )
        db.session.add(message)
        db.session.flush()
        message.recipients = [Recipient(id_recipient=1), Recipient(id_recipient=2)]
        db.session.commit()

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 2

        assert RecipientModel.has_opened(message, 1) == False
        assert message.recipients[0].has_opened == True

        assert RecipientModel.has_opened(message, 1) == True
        assert message.recipients[0].has_opened == True

        RecipientModel.set_recipients(message, [])
        db.session.query(Message).delete()
        db.session.commit()
        assert db.session.query(Message).count() == 0
