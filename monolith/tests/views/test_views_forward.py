import pytest
from flask_login import logout_user
from monolith import app
from monolith.auth import current_user
from monolith.database import Message, User, db
from monolith.forms import delivery_format
from datetime import datetime
from monolith.classes.read_messages import MessModel

class TestViewsForward():

    def test_forward_mess_not_auth(self,test_client):
        test_client.get('/logout',follow_redirects=True)
        MessModel.insert_db()
        response = test_client.get('/forwarding/1',follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be logged in to forward a message' in response.data
        MessModel.remove_db()

    def test_forward_mess_auth(self,test_client):
        test_client.get('/logout',follow_redirects=True)
        MessModel.insert_db()
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/forwarding/10',follow_redirects=True)
        assert response.status_code == 200






