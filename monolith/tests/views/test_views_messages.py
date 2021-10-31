from datetime import datetime
import http
from flask.wrappers import Response

import pytest
from http import HTTPStatus
from flask import request
from flask import url_for

from monolith.classes.user import UserModel
from monolith.classes.message import MessageModel
from monolith.database import db
from monolith.database import Message
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

    data = {'body_message': 'test message 2', 'date_of_send': '10:05 07/07/2022', 'recipient': 2}
    msg = Message(
        body_message=data['body_message'],
        date_of_send=datetime.strptime(data['date_of_send'],'%H:%M %d/%m/%Y'),
        id_sender=1,
        id_receipent=data['recipient']
    )
    MessageModel.add_draft(msg)

    test_client.get('/logout', follow_redirects=True)
    yield
    UserModel.delete_user(email=new_user['email'])
    db.session.delete(msg)
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

        data = {'body_message': draft_body, 'date_of_send': '10:05 07/07/2022', 'recipient': '2'}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check that the message was added to the table
        assert old_len + 1 == db.session.query(Message).count()

        # Check that informations inside the database are correct
        user = db.session.query(User).filter(User.email == 'example@example.com').first()
        draft_db = db.session.query(Message).order_by(Message.id_message.desc()).first()
        assert draft_db.id_message == old_len + 1
        assert draft_db.id_sender == user.id
        assert draft_db.id_receipent == 2
        assert draft_db.body_message == draft_body
        db.session.delete(draft_db)
        db.session.commit()

    def test_draft_added_wrong_fields(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        draft_body = 'test_draft'

        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        old_len = db.session.query(Message).count()

        data = {'body_message': draft_body, 'date_of_send': 'fail', 'recipient': 'fail'}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b'Not a valid' in response.data

    def test_get_draft_auth(self, test_client):
        response = test_client.get('/draft')
        assert response.status_code == 200
        assert b'Message' in response.data
        assert b'submit' in response.data

      

@pytest.mark.usefixtures('clean_db_and_logout')
class TestViewsMessagesSend:

    def test_send_message_not_logged(self, test_client):

        message = Message(id_receipent=1,
                          id_sender=1,
                          body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))

        db.session.add(message)
        db.session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))

        assert response.status_code == 401
        db.session.delete(message)
        db.session.commit()

    def test_send_message_id_wrong(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        response = test_client.post('/login', data=admin_user)

        message = Message(id_receipent=1,
                          id_sender=2,
                          body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))

        MessageModel.add_draft(message)

        response = test_client.post('/send_message/' + str(message.id_message))

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        test_client.post('/logout')
        db.session.delete(message)
        db.session.commit()

    def test_send_message(self, test_client):

        message = Message(id_receipent=1,
                          id_sender=1,
                          body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))

        MessageModel.add_draft(message)

        response = test_client.post('/send_message/' + str(message.id_message))
        assert b'Message has been sent correctly' in response.data
        db.session.delete(message)
        db.session.commit()

    def test_send_message_not_exists(wself, test_client):

        response = test_client.post('/send_message/1000')
        assert b'1000 message not found' in response.data
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.usefixtures('clean_db_and_logout', 'draft_setup')
class TestViewsMessagesDraftEdit:
    
    def test_edit_draft_not_logged_in(self, test_client):
        response = test_client.get(url_for('messages.edit_draft',id=1),follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b'Login' in response.data

    def test_edit_draft_not_found(self,test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post(url_for('auth.login'), data=admin_user)
        response = test_client.get(url_for('messages.edit_draft',id=100))
        assert response.status_code == HTTPStatus.NOT_FOUND
        test_client.post(url_for('auth.logout'))

    def test_edit_draft_not_sender(self, test_client):
        admin_user = {'email': 'example1@example1.com', 'password': 'admin1'}
        test_client.post(url_for('auth.login'), data=admin_user)
        response = test_client.get(url_for('messages.edit_draft',id=1))
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        test_client.post(url_for('auth.logout'))

    def test_get_edit_draft_logged_in(self,test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post(url_for('auth.login'), data=admin_user)
        response = test_client.get(url_for('messages.edit_draft',id=1))
        assert response.status_code == HTTPStatus.OK
        assert b'Save as Draft' in response.data
        test_client.post(url_for('auth.logout'))

    def test_post_edit_draft_ok(self,test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post(url_for('auth.login'), data=admin_user)
        draft = {'body_message':'test_edit','date_of_send':'09:15 10/01/2022','recipient':2}
        response = test_client.post(url_for('messages.edit_draft',id=1),data=draft,follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        msg = MessageModel.id_message_exists(id_message=1)
        assert msg.body_message == 'test_edit'
        test_client.post(url_for('auth.logout'))

        
    def test_post_edit_draft_incorrect_fields(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post(url_for('auth.login'), data=admin_user)
        draft = {'body_message':'test_edit','date_of_send':'fail','recipient':'fail2'}
        response = test_client.post(url_for('messages.edit_draft',id=1),data=draft,follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b'Not a valid choice' in response.data

        test_client.post(url_for('auth.logout'))