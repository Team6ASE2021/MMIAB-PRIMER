import pytest
from flask.wrappers import Response
from monolith import app
from monolith.classes import read_messages
from monolith.database import Message, User, db
import logging

class TestViewsReadMessage():

    def read_mess_not_auth(self,test_client):
        read_messages.test_insert_db()
        response = test_client.get('/read_message/1',follow_redirects=True)
        assert response.status_code == 401
        assert b'You are not allowed to' in response.data
        read_messages.test_remove_db()



        




