from typing import Optional
from monolith.database import db, Message, User
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

        #return messages_arrived
        return [{'id' : m.id_message,\
                'date' : m.date_of_send.strftime("%H:%M %d/%m/%Y"),\
                'sent': m.is_sended,\
                'received' : m.is_arrived,\
                'notified' : m.is_notified} for m in messages_arrived]

    def get_notify(user : User):
        notify_list = db.session.query(Message).filter(user.id == Message.id_receipent,\
                                                       Message.is_notified == False,\
                                                       Message.is_arrived == True,
                                                       Message.is_sended == True)

        for notify in notify_list:
            notify.is_notified = True

        db.session.commit()
        
        return notify_list
    
class NotExistingMessageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
