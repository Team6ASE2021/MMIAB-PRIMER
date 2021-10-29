from flask import signals
import pytest
from monolith import app
from monolith.auth import current_user
from monolith.database import Message, User, db
from monolith.forms import delivery_format

from datetime import datetime
import logging


class TestViewsMessages():

    logger = logging.getLogger(__name__)

    def test_post_draft_added_non_auth(self, test_client, session):
        draft_body = 'test_draft'
        data = {'body_message': draft_body}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be logged in' in response.data

    def test_get_draft_non_auth(self, test_client, session):
        response = test_client.get('/draft')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data

    def test_post_draft_added_auth(self, test_client, session):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        draft_body = 'test_draft'

        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        old_len = session.query(Message).count()

        data = {'body_message': draft_body}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check that the message was added to the table
        assert old_len + 1 == session.query(Message).count()

        # Check that informations inside the database are correct
        user = session.query(User).filter(User.email == 'example@example.com').first()
        draft_db = session.query(Message).order_by(Message.id_message.desc()).first()
        assert draft_db.id_message == old_len + 1
        assert draft_db.id_sender == user.id
        assert draft_db.body_message == draft_body

    def test_get_draft_auth(self, test_client, session):
        response = test_client.get('/draft')
        assert response.status_code == 200
        assert b'Message' in response.data
        assert b'submit' in response.data

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_send_message_not_logged(self, test_client, session, test_msg):

        session.add(test_msg)
        session.commit()

        response = test_client.post('/send_message/' + str(test_msg.id_message))

        assert response.status_code == 401

        session.delete(test_msg)
        session.commit()

    def test_send_message_id_wrong(self, test_client, session):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        response = test_client.post('/login', data=admin_user)

        message = Message(id_receipent=1,
                          id_sender=2,
                          body_message="Ciao",
                          date_of_send=datetime.strptime("01/01/2022", "%d/%m/%Y"))

        session.add(message)
        session.commit()

        response = test_client.post('/send_message/' + str(message.id_message))

        assert response.status_code == 410

        session.delete(message)
        session.commit()

    def test_send_message(self, test_client, test_msg, session, test_user):
        session.add(test_user)
        session.commit()
        user = {'email': test_user.email, 'password': 'pass'}
        response = test_client.post('/login', data=user, follow_redirects=True)
        assert response.status_code == 200
        session.add(test_msg)
        session.commit()

        response = test_client.post('/send_message/' + str(test_msg.id_message))
        assert b'Message has been sent correctly' in response.data
        test_client.get('/logout')
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()

    def test_send_message_not_exists(wself, test_client):
        response = test_client.post('/login', data={'email': 'example@example.com', 'password': 'admin'})
        response = test_client.post('/send_message/1000')
        assert b'1000 message not found' in response.data
        assert response.status_code == 411

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_draft_edit_setup(self, test_client, session, test_msg):
        session.add(test_msg)
        session.commit()

        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        response = test_client.post('/login', data=admin_user, follow_redirects=True)
        assert response.status_code == 200
        data = {'body_message': 'test message 2'}
        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200

        assert session.query(Message).order_by(Message.id_message.desc()).first().id_message == 2
        session.delete(test_msg)
        session.delete(session.query(Message).first())
        session.commit()
        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_draft_edit_message_not_existing(self, test_client, session):
        response = test_client.get('/draft/edit/100')
        assert response.status_code == 404
        assert b'Message not found' in response.data

        data = {'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        test_client.post('/draft/edit/100', data=data, follow_redirects=True)
        assert response.status_code == 404
        assert b'Message not found' in response.data

    def test_draft_edit_user_not_logged_in(self, test_client, session, test_msg):
        session.add(test_msg)
        session.commit()
        response = test_client.get('/draft/edit/1')
        assert response.status_code == 200
        assert b'Hi Anonymous' in response.data

        data = {'body_message': 'test message 1 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be logged in' in response.data
        session.delete(test_msg)

    def test_draft_edit_wrong_user(self, test_client, test_msg, session, test_user):
        session.add(test_user)
        session.add(test_msg)
        session.commit()
        new_user = {'email': "example@example.com", 'password': 'admin'}
        response = test_client.post('/login', data=new_user, follow_redirects=True)
        assert response.status_code == 200

        data = {'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 401
        assert b'You must be the sender' in response.data
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()
        response = test_client.get('/logout', follow_redirects=True)

    def test_draft_edit_empty_fields(self, test_client, test_msg, test_user, session):
        session.add(test_user)
        session.add(test_msg)
        session.commit()
        user = {'email': test_user.email, 'password': 'pass'}
        response = test_client.post('/login', data=user, follow_redirects=True)
        assert response.status_code == 200

        data = {'body_message': 'test message  edited', 'date_of_send': '', 'recipient': ''}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()
        test_client.post('/logout')

    def test_draft_edit_single_field(self, test_client, test_user, test_msg, session):
        session.add(test_user)
        session.add(test_msg)
        session.commit()
        test_client.post('/login', data={'email': test_user.email, 'password': 'pass'})
        data = {'body_message': 'test message 2', 'date_of_send': '', 'recipient': ''}
        update1 = {'body_message': 'test message 2 edited', 'date_of_send': '', 'recipient': 'example@example.com'}
        update2 = {'body_message': 'test message 2 edited',
                   'date_of_send': datetime.now().strftime(delivery_format), 'recipient': ''}

        response = test_client.post('/draft/edit/1', data=update1, follow_redirects=True)
        assert response.status_code == 200
        draft = session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update1['body_message']
        assert draft.date_of_send == None
        assert draft.id_receipent == session.query(User).filter(User.email == update1['recipient']).first().id

        response = test_client.post('/draft/edit/1', data=update2, follow_redirects=True)
        assert response.status_code == 200
        draft = session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update2['body_message']
        assert draft.date_of_send == datetime.strptime(update2['date_of_send'], delivery_format)
        assert draft.id_receipent == None
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()
        test_client.post('/logout')

    def test_draft_edit_full_fields(self, test_client, test_user, test_msg, session):
        session.add(test_user)
        session.add(test_msg)
        session.commit()
        test_client.post('/login', data={'email': test_user.email, 'password': 'pass'})
        data = {'body_message': 'test message 2 edited', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        draft = session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == datetime.strptime(data['date_of_send'], delivery_format)
        assert draft.id_receipent == session.query(User).filter(User.email == data['recipient']).first().id
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()
        test_client.post('/logout')

    def test_draft_edit_update_fields(self, test_client, test_user, test_msg, session):
        session.add(test_user)
        session.add(test_msg)
        session.commit()
        dt = datetime.now()
        dt = dt.replace(year=2022)
        data = {'body_message': 'test message 2 edited twice', 'date_of_send': dt.strftime(
            delivery_format), 'recipient': 'example@example.com'}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        draft = session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == data['body_message']
        assert draft.date_of_send == datetime.strptime(data['date_of_send'], delivery_format)
        assert draft.id_receipent == session.query(User).filter(User.email == data['recipient']).first().id
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()
        test_client.post('/logout')

    def test_draft_edit_invalid_recipient(self, test_client, test_user, test_msg, session):
        session.add(test_user)
        session.add(test_msg)
        session.commit()
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
        draft = session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update['body_message']
        assert draft.date_of_send == datetime.strptime(update['date_of_send'], delivery_format)
        assert draft.id_receipent == session.query(User).filter(User.email == data['recipient']).first().id

        draft.id_receipent = 100
        session.commit()

        response = test_client.post('/draft/edit/1', data=update, follow_redirects=True)
        assert response.status_code == 200
        draft = session.query(Message).filter(Message.id_message == 1).first()
        assert draft != None
        assert draft.body_message == update['body_message']
        assert draft.date_of_send == datetime.strptime(update['date_of_send'], delivery_format)
        assert draft.id_receipent == None
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()
        test_client.post('/logout')


    def test_draft_edit_invalid_input(self, test_client, test_user, test_msg, session):
        session.add(test_user)
        session.add(test_msg)
        draft = session.query(Message).filter(Message.id_message == 1).first()
        draft.body_message = None
        session.commit()

        data = {'body_message': '', 'date_of_send': datetime.now().strftime(delivery_format),
                'recipient': 'example@example.com'}
        data = {'body_message': 'test message 2 edited', 'date_of_send': 'wrong date', 'recipient': 'example@example.com'}

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.post('/draft/edit/1', data=data, follow_redirects=True)
        assert response.status_code == 200
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()
        test_client.post('/logout')


    def test_draft_invalid_input(self, test_client, test_user, test_msg, session):
        session.add(test_user)
        session.add(test_msg)
        session.commit()
        data = {'body_message': ''}

        response = test_client.post('/draft', data=data, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        session.delete(test_user)
        session.delete(test_msg)
        session.commit()
        test_client.post('/logout')


    def test_show_recipients(self, test_client):
        pass
