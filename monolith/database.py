from enum import unique
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

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

    #id_message is the primary key that identify a message
    id_message = db.Column(db.Integer, primary_key=True, autoincrement=True)

    #id of sender and receipent

    id_sender = db.Column(db.Integer)
    id_receipent = db.Column(db.Integer)

    #body of message and date of send
    body_message = db.Column(db.Unicode(256))
    date_of_send = db.Column(db.DateTime)

    #boolean variables that describe the state of the message
    is_sended = db.Column(db.Boolean, default = False)
    is_arrived = db.Column(db.Boolean, default = False)
    is_notified = db.Column(db.Boolean, default = False)

    # boolean flag that tells if the message must be filtered for users who resquest it
    to_filter = db.Column(db.Boolean, default = False)

    #constructor of the message object
    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)
        
