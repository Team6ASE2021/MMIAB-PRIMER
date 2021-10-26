import pytest
from monolith import app
from monolith.auth import current_user
from monolith.database import Message, User, db
from monolith.forms import delivery_format

from datetime import datetime

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

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_draft_edit_setup(self, test_client):
        if current_user.is_authenticated:
            response = test_client.get('/logout', follow_redirects=True)
            assert response.status_code == 200

        new_user = {\
                'email': 'example1@example1.com',\
                'firstname': 'jack',\
                'lastname': 'black',\
                'password': 'admin1',\
                'dateofbirth': '01/01/1990' }

        response = test_client.post('/create_user', data=new_user, follow_redirects=True)
        assert response.status_code == 200

        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        data = { 'body_message': 'test message 2'}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200       

        assert db.session.query(Message).order_by(Message.id_message.desc()).first().id_message == 2

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


    def test_draft_edit_message_not_existing(self, test_client):
        response = test_client.get('/draft/edit/100')
        assert response.status_code == 404
        assert b'Message not found' in response.data

        data = { 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        test_client.post('/draft/edit/100', data=data, follow_redirects=True)
        assert response.status_code == 404
        assert b'Message not found' in response.data

    def test_draft_edit_user_not_logged_in(self, test_client):
        response = test_client.get('/draft/edit/2')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data

        data = { 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        response = test_client.post('/draft/edit/2', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be logged in' in response.data

    def test_draft_edit_wrong_user(self, test_client):
        new_user = { 'email': 'example1@example1.com', 'password': 'admin1'}
        response = test_client.post('/login', data=new_user, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/draft/edit/2')
        assert response.status_code == 200
        assert b'it looks like' in response.data

        data = { 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        response = test_client.post('/draft/edit/2', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be the sender' in response.data

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_draft_edit_empty_fields(self, test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        data = { 'date_of_send': '', 'recipient' : '' }

        response = test_client.post('/draft/edit/2', data=data, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 2).first()
        assert draft != None
        assert draft.date_of_send == None
        assert draft.id_receipent == None

    def test_draft_edit_single_field(self, test_client):
        data = { 'date_of_send': '', 'recipient' : '' }
        update1 = { 'date_of_send': '', 'recipient' : 'example@example.com' }
        update2 = { 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : '' }

        response = test_client.post('/draft/edit/2', data=update1, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 2).first()
        assert draft != None
        assert draft.date_of_send == None
        assert draft.id_receipent == db.session.query(User).filter(User.email == update1['recipient']).first().id

        response = test_client.post('/draft/edit/2', data=update2, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 2).first()
        assert draft != None
        assert draft.date_of_send == datetime.strptime(update2['date_of_send'], delivery_format)
        assert draft.id_receipent == None 

        response = test_client.post('/draft/edit/2', data=data, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 2).first()
        assert draft != None
        assert draft.date_of_send == None
        assert draft.id_receipent == None

    def test_draft_edit_full_fields(self, test_client):
        data = { 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }

        response = test_client.post('/draft/edit/2', data=data, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 2).first()
        assert draft != None
        assert draft.date_of_send == datetime.strptime(data['date_of_send'], delivery_format)
        assert draft.id_receipent == db.session.query(User).filter(User.email == data['recipient']).first().id

    def test_draft_edit_update_fields(self, test_client):
        dt = datetime.now()
        dt = dt.replace(year = 2022)
        data = { 'date_of_send': dt.strftime(delivery_format), 'recipient' : 'example@example.com' }

        response = test_client.post('/draft/edit/2', data=data, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 2).first()
        assert draft != None
        assert draft.date_of_send == datetime.strptime(data['date_of_send'], delivery_format)
        assert draft.id_receipent == db.session.query(User).filter(User.email == data['recipient']).first().id

    def test_draft_edit_invalid_recipient(self, test_client):
        data = { 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        dt = datetime.now()
        dt = dt.replace(year = 2022)
        update = { 'date_of_send': dt.strftime(delivery_format), 'recipient' : 'none@none.com' }

        response = test_client.post('/draft/edit/2', data=data, follow_redirects=True)
        assert response.status_code == 200 
        response = test_client.post('/draft/edit/2', data=update, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 2).first()
        assert draft != None
        assert draft.date_of_send == datetime.strptime(update['date_of_send'], delivery_format)
        assert draft.id_receipent == db.session.query(User).filter(User.email == data['recipient']).first().id

        draft.id_receipent = 100
        db.session.commit()

        response = test_client.post('/draft/edit/2', data=update, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 2).first()
        assert draft != None
        assert draft.date_of_send == datetime.strptime(update['date_of_send'], delivery_format)
        assert draft.id_receipent == None















