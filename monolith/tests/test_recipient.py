import pytest
from datetime import datetime
from monolith.database import db, Message, Recipient, User
from monolith.classes.recipient import RecipientModel
from monolith.classes.user import UserModel 

@pytest.mark.usefixtures('clean_db_and_logout')
class TestRecipientModel:

    def test_recipient_change_and_delete(self):
        new_user = {
            'email': 'example1@example1.com',
            'firstname': 'jack',
            'lastname': 'black',
            'password': 'admin1',
            'dateofbirth': '01/01/1990'}

        UserModel.create_user(User(
            email=new_user['email'],
            firstname=new_user['firstname'],
            lastname=new_user['lastname'],
            dateofbirth=datetime.strptime(new_user['dateofbirth'], "%d/%m/%Y")
        ), password=new_user['password'])

        message = Message(id_sender=2,
                          body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2000", "%d/%m/%Y"))
        db.session.add(message)
        db.session.flush()
        message.recipients = [Recipient(id_recipient=1)]
        db.session.commit()

        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 1
        assert db.session.query(Message).first().recipients[0].id_recipient == db.session.query(Recipient).first().id_recipient

        message.recipients = [Recipient(id_recipient=2)]
        db.session.commit()
        assert db.session.query(Message).count() == 1
        assert db.session.query(Recipient).count() == 2
        assert db.session.query(Message).first().recipients[0].id_recipient == db.session.query(Recipient).all()[1].id_recipient
        assert db.session.query(Recipient).first().id_message == None
        assert db.session.query(Recipient).first().message == None
        assert db.session.query(Recipient).first().id_recipient == 1

        db.session.query(Message).delete()
        db.session.commit()
        assert db.session.query(Recipient).count() == 2
        for rcp in db.session.query(Recipient).all():
            assert rcp.message == None







