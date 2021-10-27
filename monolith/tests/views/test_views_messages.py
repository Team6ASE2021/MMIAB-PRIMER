import pytest
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


@pytest.mark.usefixtures('clean_db_and_logout')
class TestViewsMessagesDraft():

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
    
@pytest.mark.usefixtures('clean_db_and_logout')
class TestViewsMessagesSend:

    def test_send_message_not_logged(self, test_client):

        message = Message(id_receipent = 1, \
                          id_sender = 1, \
                          body_message = "Ciao", \
                          date_of_send = datetime.strptime("01/01/2022", "%d/%m/%Y"))
        
        db.session.add(message)
        db.session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))
        
        assert response.status_code == 401

    def test_send_message_id_wrong(self, test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user)

        message = Message(id_receipent = 1, \
                          id_sender = 2, \
                          body_message = "Ciao", \
                          date_of_send = datetime.strptime("01/01/2022", "%d/%m/%Y"))

        db.session.add(message)
        db.session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))
        
        assert response.status_code == 410

    def test_send_message(self, test_client):

        message = Message(id_receipent = 1, \
                          id_sender = 1, \
                          body_message = "Ciao", \
                          date_of_send = datetime.strptime("01/01/2022", "%d/%m/%Y"))

        db.session.add(message)
        db.session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))
        assert b'Message has been sent correctly' in response.data

    def test_send_message_not_exists(wself, test_client):

        response = test_client.post('/send_message/1000')
        assert b'1000 message not found' in response.data
        assert response.status_code == 411


@pytest.fixture(scope='class')
def draft_edit_setup(test_client):
    new_user = {\
            'email': 'example1@example1.com',\
            'firstname': 'jack',\
            'lastname': 'black',\
            'password': 'admin1',\
            'dateofbirth': '01/01/1990' }

    response = test_client.post('/create_user', data=new_user, follow_redirects=True)

    admin_user = { 'email': 'example@example.com', 'password': 'admin' }
    response = test_client.post('/login', data=admin_user, follow_redirects=True)

    data = { 'body_message': 'test message 2'}
    response = test_client.post('/draft', data=data, follow_redirects=True)

    response = test_client.get('/logout', follow_redirects=True)

@pytest.mark.usefixtures('clean_db_and_logout', 'draft_edit_setup')
class TestViewsMessagesDraftEdit:

    def test_draft_edit_message_not_existing(self, test_client):
        response = test_client.get('/draft/edit/100')
        assert response.status_code == 404
        assert b'Message not found' in response.data

        data = { 'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        test_client.post('/draft/edit/100', data=data, follow_redirects=True)
        assert response.status_code == 404
        assert b'Message not found' in response.data

    def test_draft_edit_user_not_logged_in(self, test_client):
        response = test_client.get('/draft/edit/1')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data

        data = { 'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be logged in' in response.data

    def test_draft_edit_wrong_user(self, test_client):
        new_user = { 'email': 'example1@example1.com', 'password': 'admin1'}
        response = test_client.post('/login', data=new_user, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/draft/edit/1')
        assert response.status_code == 200
        assert b'it looks like' in response.data

        data = { 'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be the sender' in response.data

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_draft_edit_empty_fields(self, test_client):
        admin_user = { 'email': 'example@example.com', 'password': 'admin' }
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        data = { 'body_message': 'test message 2 edited', 'date_of_send': '', 'recipient' : '' }

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == None
        assert draft.id_receipent == None

    def test_draft_edit_single_field(self, test_client):
        data = { 'body_message': 'test message 2', 'date_of_send': '', 'recipient' : '' }
        update1 = { 'body_message': 'test message 2 edited', 'date_of_send': '', 'recipient' : 'example@example.com' }
        update2 = { 'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : '' }

        response = test_client.post('/draft/edit/1', data=update1, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update1['body_message']
        assert draft.date_of_send == None
        assert draft.id_receipent == db.session.query(User).filter(User.email == update1['recipient']).first().id

        response = test_client.post('/draft/edit/1', data=update2, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update2['body_message']
        assert draft.date_of_send == datetime.strptime(update2['date_of_send'], delivery_format)
        assert draft.id_receipent == None 

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == None
        assert draft.id_receipent == None

    def test_draft_edit_full_fields(self, test_client):
        data = { 'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == datetime.strptime(data['date_of_send'], delivery_format)
        assert draft.id_receipent == db.session.query(User).filter(User.email == data['recipient']).first().id

    def test_draft_edit_update_fields(self, test_client):
        dt = datetime.now()
        dt = dt.replace(year = 2022)
        data = { 'body_message': 'test message 2 edited twice', 'date_of_send': dt.strftime(delivery_format), 'recipient' : 'example@example.com' }

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == datetime.strptime(data['date_of_send'], delivery_format)
        assert draft.id_receipent == db.session.query(User).filter(User.email == data['recipient']).first().id

    def test_draft_edit_invalid_recipient(self, test_client):
        data = { 'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        dt = datetime.now()
        dt = dt.replace(year = 2022)
        update = { 'body_message': 'test message 2 edited', 'date_of_send': dt.strftime(delivery_format), 'recipient' : 'none@none.com' }

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200 
        response = test_client.post('/draft/edit/1', data=update, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update['body_message']
        assert draft.date_of_send == datetime.strptime(update['date_of_send'], delivery_format)
        assert draft.id_receipent == db.session.query(User).filter(User.email == data['recipient']).first().id

        draft.id_receipent = 100
        db.session.commit()

        response = test_client.post('/draft/edit/1', data=update, follow_redirects=True)
        assert response.status_code == 200 
        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update['body_message']
        assert draft.date_of_send == datetime.strptime(update['date_of_send'], delivery_format)
        assert draft.id_receipent == None

    def test_draft_edit_invalid_input(self, test_client):

        draft = db.session.query(Message).filter(Message.id_message == 1).first()
        draft.body_message = None
        db.session.commit()

        data = { 'body_message': '', 'date_of_send': datetime.now().strftime(delivery_format), 'recipient' : 'example@example.com' }
        data = { 'body_message': 'test message 2 edited', 'date_of_send': 'wrong date', 'recipient' : 'example@example.com' }

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200 

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200 

    def test_draft_invalid_input(self, test_client):
        data = { 'body_message': ''}

        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200 




