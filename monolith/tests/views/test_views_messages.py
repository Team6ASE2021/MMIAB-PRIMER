from datetime import datetime

import pytest
from http import HTTPStatus
from flask import request
from flask import url_for

from monolith.classes.user import UserModel
from monolith.classes.message import MessageModel
from monolith.classes.recipient import RecipientModel
from monolith.database import db
from monolith.database import Message
from monolith.database import Recipient
from monolith.database import User


@pytest.fixture(scope='class')
def draft_setup(test_client):
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

    admin_user = {'email': 'example@example.com', 'password': 'admin'}
    test_client.post('/login', data=admin_user, follow_redirects=True)

    data = {'body_message': 'test message 2', 'date_of_send': '10:05 07/07/2022', 'recipients-0-recipient': '2'}
    msg = Message(
        body_message=data['body_message'],
        date_of_send=datetime.strptime(data['date_of_send'], '%H:%M %d/%m/%Y'),
        id_sender=1
    )
    MessageModel.add_draft(msg)
    RecipientModel.set_recipients(msg, [2])

    test_client.get('/logout', follow_redirects=True)
    yield
    MessageModel.delete_message(msg.id_message)
    db.session.query(Recipient).delete()
    db.session.commit()


@pytest.mark.usefixtures('clean_db_and_logout', 'draft_setup')
class TestViewsMessagesDraft:

    def test_post_draft_added_non_auth(self, test_client):

        draft_body = 'test_draft'
        data = {'body_message': draft_body}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert request.path == url_for('auth.login')

    def test_get_draft_non_auth(self, test_client):
        response = test_client.get('/draft', follow_redirects=True)
        assert response.status_code == 200
        assert request.path == url_for('auth.login')

    def test_post_draft_added_auth(self, test_client):

        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        draft_body = 'test_draft'

        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        old_len = db.session.query(Message).count()

        data = {'body_message': draft_body, 'date_of_send': '10:05 07/07/2022', 'recipients-0-recipient': '2'}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check that the message was added to the table
        assert old_len + 1 == db.session.query(Message).count()

        # Check that informations inside the database are correct
        user = db.session.query(User).filter(User.email == 'example@example.com').first()
        draft_db = db.session.query(Message).order_by(Message.id_message.desc()).first()
        assert draft_db.id_message == old_len + 1
        assert draft_db.id_sender == user.id
        assert draft_db.recipients[0].id_recipient == 2
        assert draft_db.body_message == draft_body
        db.session.delete(draft_db)
        db.session.commit()

    def test_draft_added_wrong_fields(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        draft_body = 'test_draft'

        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        old_len = db.session.query(Message).count()

        data = {'body_message': draft_body, 'date_of_send': 'fail', 'recipients-0-recipient': 'fail'}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b'Not a valid' in response.data

    def test_get_draft_auth(self, test_client):
        response = test_client.get('/draft')
        assert response.status_code == 200
        assert b'Message' in response.data
        assert b'submit' in response.data

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


@pytest.mark.usefixtures('clean_db_and_logout')
class TestViewsMessagesSend:

    def test_send_message_not_logged(self, test_client):

        message = Message(id_sender=1,
                          body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))

        db.session.add(message)
        db.session.flush()
        message.recipients.append(Recipient(id_recipient=1))
        db.session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))

        assert response.status_code == 401
        db.session.delete(message)
        db.session.commit()

    def test_send_message_id_wrong(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        response = test_client.post('/login', data=admin_user)

        message = Message(id_sender=2,
                          body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))
        MessageModel.add_draft(message)
        RecipientModel.add_recipients(message, [1])

        response = test_client.post('/send_message/' + str(message.id_message))

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        test_client.post('/logout')
        db.session.delete(message)
        db.session.commit()

    def test_send_message(self, test_client):

        message = Message(id_sender=1,
                          body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))
        MessageModel.add_draft(message)
        RecipientModel.add_recipients(message, [1])

        response = test_client.post('/send_message/' + str(message.id_message))
        assert b'Message has been sent correctly' in response.data
        db.session.delete(message)
        db.session.commit()

    def test_send_message_not_exists(wself, test_client):

        response = test_client.post('/send_message/1000')
        assert b'1000 message not found' in response.data
        assert response.status_code == HTTPStatus.NOT_FOUND


"""
@pytest.fixture(scope='class')
def draft_edit_setup(test_client):
    new_user = {
        'email': 'example1@example1.com',
        'firstname': 'jack',
        'lastname': 'black',
        'password': 'admin1',
        'dateofbirth': '01/01/1990'}

    response = test_client.post('/create_user', data=new_user, follow_redirects=True)

    admin_user = {'email': 'example@example.com', 'password': 'admin'}
    response = test_client.post('/login', data=admin_user, follow_redirects=True)

    data = {'body_message': 'test message 2'}
    response = test_client.post('/draft', data=data, follow_redirects=True)

    response = test_client.get('/logout', follow_redirects=True)


@pytest.mark.usefixtures('clean_db_and_logout', 'draft_edit_setup')
class TestViewsMessagesDraftEdit:

    def test_draft_edit_message_not_existing(self, test_client):
        response = test_client.get('/draft/edit/100')
        assert response.status_code == 404
        assert b'Message not found' in response.data

        data = {'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        test_client.post('/draft/edit/100', data=data, follow_redirects=True)
        assert response.status_code == 404
        assert b'Message not found' in response.data

    def test_draft_edit_user_not_logged_in(self, test_client):
        response = test_client.get('/draft/edit/1')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data

        data = {'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be logged in' in response.data

    def test_draft_edit_wrong_user(self, test_client):
        new_user = {'email': 'example1@example1.com', 'password': 'admin1'}
        response = test_client.post('/login', data=new_user, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/draft/edit/1')
        assert response.status_code == 200
        assert b'it looks like' in response.data

        data = {'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be the sender' in response.data

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_draft_edit_empty_fields(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        data = {'body_message': 'test message 2 edited', 'date_of_send': '', 'recipient': ''}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == None
        assert len(draft.recipients) == 0

    def test_draft_edit_single_field(self, test_client):
        data = {'body_message': 'test message 2', 'date_of_send': '', 'recipient': ''}
        update1 = {'body_message': 'test message 2 edited', 'date_of_send': '', 'recipient': 'example@example.com'}
        update2 = {'body_message': 'test message 2 edited',
                   'date_of_send': datetime.now().strftime(delivery_format), 'recipient': ''}

        response = test_client.post('/draft/edit/1', data=update1, follow_redirects=True)
        assert response.status_code == 200
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update1['body_message']
        assert draft.date_of_send == None
        assert draft.recipients == [db.session.query(User).filter(User.email == update1['recipient']).first().id]

        response = test_client.post('/draft/edit/1', data=update2, follow_redirects=True)
        assert response.status_code == 200
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update2['body_message']
        assert draft.date_of_send == datetime.strptime(update2['date_of_send'], delivery_format)
        assert len(draft.recipients) == 0

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == None
        assert len(draft.recipients) == 0

    def test_draft_edit_full_fields(self, test_client):
        data = {'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == datetime.strptime(data['date_of_send'], delivery_format)
        assert draft.recipients == [db.session.query(User).filter(User.email == data['recipient']).first().id]

    def test_draft_edit_update_fields(self, test_client):
        dt = datetime.now()
        dt = dt.replace(year=2022)
        data = {'body_message': 'test message 2 edited twice', 'date_of_send': dt.strftime(
            delivery_format), 'recipient': 'example@example.com'}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == datetime.strptime(data['date_of_send'], delivery_format)
        assert draft.recipients == [db.session.query(User).filter(User.email == data['recipient']).first().id]

    def test_draft_edit_invalid_recipient(self, test_client):
        data = {'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        dt = datetime.now()
        dt = dt.replace(year=2022)
        update = {'body_message': 'test message 2 edited', 'date_of_send': dt.strftime(
            delivery_format), 'recipient': 'none@none.com'}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.post('/draft/edit/1', data=update, follow_redirects=True)
        assert response.status_code == 200
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update['body_message']
        assert draft.date_of_send == datetime.strptime(update['date_of_send'], delivery_format)
        assert draft.recipients == [db.session.query(User).filter(User.email == data['recipient']).first().id]

        draft.recipients = [100]
        db.session.commit()

        response = test_client.post('/draft/edit/1', data=update, follow_redirects=True)
        assert response.status_code == 200
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update['body_message']
        assert draft.date_of_send == datetime.strptime(update['date_of_send'], delivery_format)
        assert len(draft.recipients) == 0

    def test_draft_edit_invalid_input(self, test_client):

        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        draft.body_message = None
        db.session.commit()

        data = {'body_message': '', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        data = {'body_message': 'test message 2 edited', 'date_of_send': 'wrong date', 'recipient': 'example@example.com'}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200

    def test_draft_invalid_input(self, test_client):
        data = {'body_message': ''}

        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200

        assert response.status_code == HTTPStatus.NOT_FOUND
"""


@pytest.mark.usefixtures('clean_db_and_logout', 'draft_setup')
class TestViewsMessagesDraftEdit:

    def test_edit_draft_not_logged_in(self, test_client):
        response = test_client.get(url_for('messages.edit_draft', id=1), follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b'Login' in response.data

    def test_edit_draft_not_found(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post(url_for('auth.login'), data=admin_user)
        response = test_client.get(url_for('messages.edit_draft', id=100))
        assert response.status_code == HTTPStatus.NOT_FOUND
        test_client.post(url_for('auth.logout'))

    def test_edit_draft_not_sender(self, test_client):
        admin_user = {'email': 'example1@example1.com', 'password': 'admin1'}
        test_client.post(url_for('auth.login'), data=admin_user)
        response = test_client.get(url_for('messages.edit_draft', id=1))
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        test_client.post(url_for('auth.logout'))

    def test_get_edit_draft_logged_in(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post(url_for('auth.login'), data=admin_user)
        response = test_client.get(url_for('messages.edit_draft', id=1))
        assert response.status_code == HTTPStatus.OK
        assert b'Save as Draft' in response.data
        test_client.post(url_for('auth.logout'))

    def test_post_edit_draft_ok(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post(url_for('auth.login'), data=admin_user)
        draft = {'body_message': 'test_edit', 'date_of_send': '09:15 10/01/2022', 'recipients-0-recipient': '2'}
        response = test_client.post(url_for('messages.edit_draft', id=1), data=draft, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        msg = MessageModel.id_message_exists(id_message=1)
        assert msg.body_message == 'test_edit'
        test_client.post(url_for('auth.logout'))

    def test_post_edit_draft_incorrect_fields(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post(url_for('auth.login'), data=admin_user)
        draft = {'body_message': 'test_edit', 'date_of_send': 'fail', 'recipients-0-recipient': 'fail2'}
        response = test_client.post(url_for('messages.edit_draft', id=1), data=draft, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b'Not a valid choice' in response.data

        test_client.post(url_for('auth.logout'))


@pytest.mark.usefixtures('clean_db_and_logout', 'draft_setup')
class TestViewsMessagesDeleteReadMessage:

    def test_delete_mess_not_auth(self, test_client):
        resp = test_client.get(url_for('messages.delete_message', id=1), follow_redirects=True)
        assert resp.status_code == HTTPStatus.OK
        assert b'Login' in resp.data

    def test_delete_mess_not_exists(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post('/login', data=admin_user, follow_redirects=True)
        response = test_client.get(url_for('messages.delete_message', id=1000))
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert b'Message not found' in response.data

    def test_delete_mess_not_recipient(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post('/login', data=admin_user, follow_redirects=True)
        response = test_client.get(url_for('messages.delete_message', id=1))
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert b'You are not allowed to delete this message' in response.data

    def test_delete_mess_not_arrived_yet(self, test_client):
        user = {'email': 'example1@example1.com', 'password': 'admin1'}
        message = Message(body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))
        MessageModel.add_draft(message)
        RecipientModel.set_recipients(message, [2])

        test_client.post('/login', data=user, follow_redirects=True)
        response = test_client.get(url_for('messages.delete_message', id=2), follow_redirects=True)
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert b'You are not allowed to delete this message' in response.data
        MessageModel.delete_message(2)

    def test_delete_mess_ok(self, test_client):
        user = {'email': 'example1@example1.com', 'password': 'admin1'}
        message = Message(body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))
        MessageModel.add_draft(message)
        RecipientModel.add_recipients(message, [2])

        test_client.post('/login', data=user, follow_redirects=True)
        message.is_arrived = True
        db.session.commit()
        response = test_client.get(url_for('messages.delete_message', id=message.id_message), follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b'Message succesfully deleted' in response.data

