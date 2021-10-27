import pytest
from flask.wrappers import Response
from monolith import app
from monolith.classes.read_messages import MessModel
from monolith.database import Message, User
import logging


class TestViewsReadMessage():

    def test_read_mess_not_auth(self,test_client):
        test_client.get('/logout',follow_redirects=True)
        MessModel.insert_db()
        response = test_client.get('/read_message/1',follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be logged into read the message' in response.data
        MessModel.remove_db()

    
    def test_read_mess_anonymous(self,test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        MessModel.insert_db()
        response = test_client.get('/read_message/3',follow_redirects=True)
        assert response.status_code == 200
        assert b'Anonymous' in response.data
        MessModel.remove_db()
        test_client.get('/logout',follow_redirects=True)



        




