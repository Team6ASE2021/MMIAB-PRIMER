from typing import Optional
from monolith.database import db, Message

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
        db.session.query(Message).filter_by(id_message=id).update(
            {
                Message.id_receipent:msg.id_receipent,
                Message.body_message:msg.body_message,
                Message.date_of_send:msg.date_of_send,
            }
            
        )
        db.session.commit()
    @staticmethod 
    def send_message(id_message):
        db.session.query(Message).filter(Message.id_message == id_message)\
                                 .update({Message.is_sended : 1})
        db.session.commit()


class NotExistingMessageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)