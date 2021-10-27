import pytest
from flask_login import logout_user
from monolith import app
from monolith.auth import current_user
from monolith.database import Message, User, db
from monolith.forms import delivery_format

from datetime import datetime

@pytest.fixture(scope='class')
def clean_db_and_logout(request, test_client):

    def _finalizer():
        test_client.get('/logout')

        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        db.session.query(User).filter(User.email != admin_user['email']).delete()
        db.session.query(Message).delete()
        db.session.commit()

    request.addfinalizer(_finalizer)


@pytest.fixture(scope='class')
def test_mailbox_setup(test_client):
    new_user = {\
            'email': 'example1@example1.com',\
            'firstname': 'jack',\
            'lastname': 'black',\
            'password': 'admin1',\
            'dateofbirth': '01/01/1990' }
    admin_user = { 'email': 'example@example.com', 'password': 'admin' }

    db.session.query(User).filter(User.email != admin_user['email']).delete()
    db.session.query(Message).delete()
    db.session.commit()

    test_client.post('/create_user', data=new_user, follow_redirects=True)

    admin_id = db.session.query(User).filter(User.email == admin_user['email']).first().id
    new_user_id = db.session.query(User).filter(User.email == new_user['email']).first().id

    admin_draft1 = Message()
    admin_draft1.body_message = 'admin draft 1'
    admin_draft1.id_sender = admin_id
    admin_draft1.id_receipent = new_user_id
    db.session.add(admin_draft1)

    admin_draft2 = Message()
    admin_draft2.body_message = 'admin draft 2'
    admin_draft2.id_sender = admin_id
    admin_draft2.id_receipent = new_user_id
    db.session.add(admin_draft2)

    admin_sent1 = Message()
    admin_sent1.body_message = 'admin send 1'
    admin_sent1.id_sender = admin_id
    admin_sent1.id_receipent = new_user_id
    admin_sent1.date_of_send = datetime.now()
    admin_sent1.is_sended = True
    db.session.add(admin_sent1)

    admin_sent2 = Message()
    admin_sent2.body_message = 'admin send 2'
    admin_sent2.id_sender = admin_id
    admin_sent2.id_receipent = new_user_id
    admin_sent2.date_of_send = datetime.now()
    admin_sent2.is_sended = True
    admin_sent2.is_received = True
    db.session.add(admin_sent2)

    admin_sent3 = Message()
    admin_sent3.body_message = 'admin send 3'
    admin_sent3.id_sender = admin_id
    admin_sent3.id_receipent = new_user_id
    admin_sent3.date_of_send = datetime.now()
    admin_sent3.is_sended = True
    admin_sent3.is_received = True
    db.session.add(admin_sent3)

    new_user_draft1 = Message()
    new_user_draft1.body_message = 'new_user draft 1'
    new_user_draft1.id_sender = new_user_id
    new_user_draft1.id_receipent = admin_id
    db.session.add(new_user_draft1)

    new_user_draft2 = Message()
    new_user_draft2.body_message = 'new_user draft 2'
    new_user_draft2.id_sender = new_user_id
    new_user_draft2.id_receipent = admin_id
    db.session.add(new_user_draft2)

    new_user_draft3 = Message()
    new_user_draft3.body_message = 'new_user draft 3'
    new_user_draft3.id_sender = new_user_id
    new_user_draft3.id_receipent = admin_id
    db.session.add(new_user_draft3)

    new_user_sent1 = Message()
    new_user_sent1.body_message = 'new_user send 1'
    new_user_sent1.id_sender = new_user_id
    new_user_sent1.id_receipent = admin_id
    new_user_sent1.date_of_send = datetime.now()
    new_user_sent1.is_sended = True
    db.session.add(new_user_sent1)

    new_user_sent2 = Message()
    new_user_sent2.body_message = 'new_user send 2'
    new_user_sent2.id_sender = new_user_id
    new_user_sent2.id_receipent = admin_id
    new_user_sent2.date_of_send = datetime.now()
    new_user_sent2.is_sended = True
    new_user_sent2.is_received = True
    db.session.add(new_user_sent2)

    new_user_sent3 = Message()
    new_user_sent3.body_message = 'new_user send 3'
    new_user_sent3.id_sender = new_user_id
    new_user_sent3.id_receipent = admin_id
    new_user_sent3.date_of_send = datetime.now()
    new_user_sent3.is_sended = True
    new_user_sent3.is_received = True
    db.session.add(new_user_sent3)

    new_user_sent4 = Message()
    new_user_sent4.body_message = 'new_user send 4'
    new_user_sent4.id_sender = new_user_id
    new_user_sent4.id_receipent = admin_id
    new_user_sent4.date_of_send = datetime.now()
    new_user_sent4.is_sended = True
    new_user_sent4.is_received = True
    db.session.add(new_user_sent4)

    db.session.commit()




@pytest.mark.usefixtures("test_mailbox_setup", "clean_db_and_logout")
class TestViewsMailbox():
    def test_mailbox_not_logged(self, test_client):
        response = test_client.get('/message/list/received')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data

        response = test_client.get('/message/list/sent')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data

        response = test_client.get('/message/list/draft')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data


    def test_mailbox_count(self, test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200       

        db_count = db.session.query(Message).filter(Message.id_receipent == current_user.id and Message.is_arrived == True).count()
        response = test_client.get('/message/list/received')
        assert response.status_code == 200
        assert response.data.count('div class="message_received"') == db_count

        db_count = db.session.query(Message).filter(Message.id_sender == current_user.id and Message.is_sended == True).count()
        response = test_client.get('/message/list/sent')
        assert response.status_code == 200
        assert response.data.count('div class="message_sent"') == db_count

        db_count = db.session.query(Message).filter(Message.id_sender == current_user.id and Message.is_sended == False).count()
        response = test_client.get('/message/list/draft')
        assert response.status_code == 200
        assert response.data.count('div class="draft"') == db_count



