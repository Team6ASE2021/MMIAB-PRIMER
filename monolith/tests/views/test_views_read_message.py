import pytest
from flask.wrappers import Response
from monolith import app
from monolith.database import Message, User, db
import logging


@pytest.mark.usefixtures('clean_db_and_logout', 'messages_setup')
class TestViewsReadMessage():

    def test_read_mess_not_auth(self,test_client):
        test_client.get('/logout',follow_redirects=True)

        response = test_client.get('/read_message/1')
        assert response.status_code == 200 
        assert b'Hey Anonymous' in response.data

    def test_read_mess_not_existing(self,test_client):
        # logger = logging.getLogger(__name__)
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/read_message/100')
        assert response.status_code == 404
        assert b'Message not found' in response.data

        test_client.get('/logout')

    def test_read_mess_from_anonymous(self,test_client):
        # logger = logging.getLogger(__name__)
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        db.session.query(Message).filter(Message.id_message == 10).update({Message.id_sender: 8})
        db.session.commit()

        response = test_client.get('/read_message/10')
        assert response.status_code == 200
        assert b'Anonymous' in response.data

        test_client.get('/logout')

    def test_read_mess_not_for_you(self,test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/read_message/9')
        assert response.status_code == 200
        assert b'you are not allowed to read this message' in response.data
        test_client.get('/logout')

    def test_read_draft_not_me(self,test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/read_message/6',follow_redirects=True)
        assert response.status_code == 200
        assert b'you are not allowed to read this message' in response.data
        test_client.get('/logout',follow_redirects=True)



        




