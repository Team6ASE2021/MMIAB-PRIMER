import unittest
from monolith import app
from monolith.database import Message, User, db
from monolith.forms import MessageForm

app.testing = True

class TestViewsMessages(unittest.TestCase):

    def setUp(self):
        app.config['WTF_CSRF_ENABLED'] = False 

    def test_draft(self):
        tested_app = app.test_client()
        TESTUSER = ('Admin', 'Admin')
        
        with app.test_request_context('/draft'):
            old_len = db.session.query(Message).count()
            user = db.session.query(User).filter(User.firstname == TESTUSER[0] and User.lastname == TESTUSER[1]).first()
            draft = Message(body_message='test draft', id_sender=user.id)
            form = MessageForm(obj=draft)
            print(form.body_message.data)
            response = tested_app.post('/draft', data=form.data, follow_redirects=True)

            self.assertEqual(old_len, db.session.query(Message).count() - 1)





