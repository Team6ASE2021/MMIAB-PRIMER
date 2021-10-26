import pytest
from monolith import app
from monolith.database import Message, User, db
import datetime

class TestViewsMessages():

    def test_post_draft_added_non_auth(self, test_client):
        draft_body= 'test_draft'
        data = { 'body_message': draft_body }
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be logged in' in response.data

    def test_get_draft_non_auth(self, test_client):
        response = test_client.get('/draft')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data

    def test_post_draft_added_auth(self, test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        draft_body= 'test_draft'
 
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200       

        old_len = db.session.query(Message).count()

        data = { 'body_message': draft_body }
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200       

        # Check that the message was added to the table
        assert old_len + 1  == db.session.query(Message).count()

        # Check that informations inside the database are correct
        user = db.session.query(User).filter(User.email == 'example@example.com').first()
        draft_db = db.session.query(Message).order_by(Message.id_message.desc()).first()
        assert draft_db.id_message == old_len + 1
        assert draft_db.id_sender == user.id
        assert draft_db.body_message == draft_body

    def test_get_draft_auth(self, test_client):
        response = test_client.get('/draft')
        assert response.status_code == 200
        assert b'Message' in response.data
        assert b'submit' in response.data

    def test_send_message_not_logged(self, test_client):
        test_client.get('/logout')

        message = Message(id_receipent = 1, \
                          id_sender = 1, \
                          body_message = "Ciao", \
                          date_of_send = datetime.datetime.strptime("01/01/2022", "%d/%m/%Y"))

        db.session.add(message)
        db.session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))
        
        assert response.status_code == 401

        db.session.delete(message)
        db.session.commit()

    def test_send_message_id_wrong(self, test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user)

        message = Message(id_receipent = 1, \
                          id_sender = 2, \
                          body_message = "Ciao", \
                          date_of_send = datetime.datetime.strptime("01/01/2022", "%d/%m/%Y"))

        db.session.add(message)
        db.session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))
        
        assert response.status_code == 410

        db.session.delete(message)
        db.session.commit()

    def test_send_message(self, test_client):

        message = Message(id_receipent = 1, \
                          id_sender = 1, \
                          body_message = "Ciao", \
                          date_of_send = datetime.datetime.strptime("01/01/2022", "%d/%m/%Y"))

        db.session.add(message)
        db.session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))
        assert b'Message has been sent correctly' in response.data

        db.session.delete(message)
        db.session.commit()

    def test_send_message_not_exists(wself, test_client):

        response = test_client.post('/send_message/1000')
        assert b'1000 message not found' in response.data
        assert response.status_code == 411