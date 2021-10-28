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
        
        messages = db.session.query(Message).filter((Message.is_sended == 1) and \
                                                    (Message.is_arrived == 0) and \
                                                    (Message.date_of_send is not None))
        messages_arrived = []
        for message in messages:
            
            time_delta = (message.date_of_send - datetime.datetime.now()).total_seconds()

            if time_delta <= 0:
                db.session.query(Message).filter(Message.id_message == message.id_message).update({Message.is_arrived : 1})
                messages_arrived.append(message)

        db.session.commit()
        return messages_arrived

class NotExistingMessageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)