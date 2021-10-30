from typing import Optional
from monolith.database import db, Message
import datetime

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
    def send_message(id_message):
        db.session.query(Message).filter(Message.id_message == id_message)\
                                 .update({Message.is_sended : 1})
        db.session.commit()

    @staticmethod
    def arrived_message():
        
        messages = db.session.query(Message).filter(Message.is_sended == True,\
                Message.is_arrived == False,\
                Message.date_of_send is not None)

        messages_arrived = []
        for m in messages:
            if (m.date_of_send - datetime.datetime.now()).total_seconds() <= 0:
                m.is_arrived = True
                messages_arrived.append(m)
        
        db.session.commit()

        # return messages_arrived
        return [{'id' : m.id_message,\
                'date' : m.date_of_send.strftime("%H:%M %d/%m/%Y"),\
                'sent': m.is_sended,\
                'received' : m.is_arrived} for m in messages_arrived]

    @staticmethod
    def create_message(id_sender=1, id_receipent=1, body_message="", date_of_send=None, is_sended=False, is_arrived=False):
        new_msg = Message()
        new_msg.id_sender = id_sender
        new_msg.id_receipent = id_receipent
        new_msg.body_message = body_message
        new_msg.date_of_send = date_of_send
        new_msg.is_sended = is_sended
        new_msg.is_arrived = is_arrived

        db.session.add(new_msg)
        db.session.commit()

        return new_msg

class NotExistingMessageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
