import re
from typing import Optional
from monolith.database import db, Message, User, Recipient
from datetime import datetime
import string
from os import path
from typing import List
from sqlalchemy import and_

class ContentFilter:
    __UNSAFE_WORDS = []
    __alphanumeric = string.ascii_letters + string.digits

    @staticmethod
    def unsafe_words():
        """
        Populates unsafe_words list with the contents of a file in monolith/static/txt folder
        if the list is still empty.
        """
        if len(ContentFilter.__UNSAFE_WORDS) == 0:
            _dir = path.dirname(path.abspath(__file__))
            with open(path.join(_dir, '../static/txt/unsafe_words.txt'), 'r') as f:
                lines = f.readlines()
                for l in lines:
                    ContentFilter.__UNSAFE_WORDS.append(l.strip())
        return ContentFilter.__UNSAFE_WORDS

    @staticmethod
    def filter_content(message_body) -> bool:
        _body = message_body.lower()
        for uw in ContentFilter.unsafe_words():
            index = _body.find(uw)
            while index >=0:
                if ((index > 0 and _body[index - 1] not in ContentFilter.__alphanumeric) or index == 0) and\
                        ((index + len(uw) < len(_body) and _body[index + len(uw)] not in ContentFilter.__alphanumeric) or index + len(uw) == len(_body)):
                    return True

                index = _body.find(uw, index + 1)

        return False
    


class MessageModel:
    """
        Wrapper class  for all db operations involving message
    """

    @staticmethod
    def id_message_exists(id_message) -> Optional[Message]:
        #get the message from database
        message = db.session.query(Message).filter(Message.id_message == id_message).first()
        
        if message is None:
            raise NotExistingMessageError(str(id_message) + " message not found")
        else:
            return message
    @staticmethod
    def add_draft(msg: Message) -> None:
        db.session.add(msg)
        db.session.commit()
    
    @staticmethod
    def update_draft(id: int, msg:Message):
        db.session.query(Message).filter(Message.id_message == id).update(
            {
                Message.body_message:msg.body_message,
                Message.date_of_send:msg.date_of_send
            }
            
        )
        db.session.commit()

    @staticmethod 
    def send_message(id_message):
        db.session.query(Message).filter(Message.id_message == id_message)\
                                 .update({Message.is_sent : 1})
        db.session.commit()

    @staticmethod
    def arrived_message():
        
        messages = db.session.query(Message).filter(Message.is_sent == True,\
                Message.is_arrived == False,\
                Message.date_of_send is not None)

        messages_arrived = []
        for m in messages:
            if (m.date_of_send - datetime.now()).total_seconds() <= 0:
                m.is_arrived = True
                messages_arrived.append(m)
        
        db.session.commit()

        #return messages_arrived
        return [{'id' : m.id_message,\
                'date' : m.date_of_send.strftime("%H:%M %d/%m/%Y"),\
                'sent': m.is_sent,\
                'received' : m.is_arrived,\
                'notified' : [(rcp.id_recipient, rcp.is_notified) for rcp in m.recipients]} for m in messages_arrived]

    @staticmethod
    def get_notify(user : User):
        notify_list = db.session.query(Recipient).\
                filter(Recipient.id_recipient == user.id, Recipient.is_notified == False).\
                filter(Recipient.message.has(and_(Message.is_arrived == True, Message.is_sent == True))).all()
        """
        notify_list = db.session.query(Message).\
                filter(Message.is_arrived == True, Message.is_sent == True).\
                filter(Message.recipients.any(and_(Recipient.id_recipient == user.id, Recipient.is_notified == False))).all()
        """

        print('pippo', [mr.id_message for mr in notify_list])

        for notify in notify_list:
            notify.is_notified = True

        db.session.commit()
        
        return notify_list
 
    @staticmethod
    def create_message(id_sender: int,
            body_message: str,
            recipients: List[int] = [],
            date_of_send: datetime = datetime.now(),
            is_sent = False,
            is_arrived = False,
            is_notified = False,
            to_filter = False):

        message = Message()
        message.id_sender = id_sender
        message.body_message = body_message
        message.date_of_send = date_of_send
        message.is_sent = is_sent
        message.is_arrived = is_arrived
        message.is_notified = is_notified
        message.to_filter = to_filter

        db.session.add(message)
        db.session.flush()

        for recipient_id in recipients:
            message.recipients.append(Recipient(id_recipient=recipient_id))

        db.session.commit()

        return message
   
    @staticmethod
    def delete_message(id_message: int):
        mess = MessageModel.id_message_exists(id_message)
        db.session.query(Recipient).filter(Recipient.id_message == mess.id_message).delete()
        db.session.commit()
        db.session.delete(mess)
        db.session.commit()

class NotExistingMessageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
