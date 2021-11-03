from enum import unique
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from typing import List

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    nickname = db.Column(db.Unicode(128),unique=False)
    location = db.Column(db.Unicode(128))
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    content_filter = db.Column(db.Boolean, default=False)
    blacklist = db.Column(db.Unicode(128))

    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False
    
    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id

class Message(db.Model):

    __tablename__ = 'message'

    _recipients_separator = '|'

    #id_message is the primary key that identify a message
    id_message = db.Column(db.Integer, primary_key=True, autoincrement=True)

    #id of sender
    id_sender = db.Column(db.Integer)
    #recipients
    recipients = db.relationship('Recipient', back_populates='message')

    #body of message and date of send
    body_message = db.Column(db.Unicode(256))
    date_of_send = db.Column(db.DateTime)

    #boolean variables that describe the state of the message
    is_sent = db.Column(db.Boolean, default = False)
    is_arrived = db.Column(db.Boolean, default = False)

    # boolean flag that tells if the message must be filtered for users who resquest it
    to_filter = db.Column(db.Boolean, default = False)

    #constructor of the message object
    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)
       
class Recipient(db.Model):
    __tablename__ = 'recipient'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_message = db.Column(db.ForeignKey('message.id_message'))
    id_recipient = db.Column(db.ForeignKey('user.id'))
    #id_message = db.Column(db.ForeignKey('message.id_message'), primary_key=True)
    #id_recipient = db.Column(db.ForeignKey('user.id'), primary_key=True)
    is_notified = db.Column(db.Boolean, default = False)
    message = db.relationship("Message", back_populates="recipients")
    user = db.relationship("User")
