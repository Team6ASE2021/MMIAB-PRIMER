import string
from datetime import datetime
from os import path
from typing import List
from typing import Optional

from sqlalchemy import and_

from monolith.database import db
from monolith.database import Message
from monolith.database import Recipient
from monolith.database import User


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
            with open(path.join(_dir, "../static/txt/unsafe_words.txt"), "r") as f:
                lines = f.readlines()
                for l in lines:
                    ContentFilter.__UNSAFE_WORDS.append(l.strip())
        return ContentFilter.__UNSAFE_WORDS

    @staticmethod
    def filter_content(message_body) -> bool:
        _body = message_body.lower()
        for uw in ContentFilter.unsafe_words():
            index = _body.find(uw)
            while index >= 0:
                if (
                    (index > 0 and _body[index - 1] not in ContentFilter.__alphanumeric)
                    or index == 0
                ) and (
                    (
                        index + len(uw) < len(_body)
                        and _body[index + len(uw)] not in ContentFilter.__alphanumeric
                    )
                    or index + len(uw) == len(_body)
                ):
                    return True

                index = _body.find(uw, index + 1)

        return False


class MessageModel:
    """
    Wrapper class  for all db operations involving message
    """

    @staticmethod
    def id_message_exists(id_message) -> Optional[Message]:
        # get the message from database
        message = (
            db.session.query(Message).filter(Message.id_message == id_message).first()
        )

        if message is None:
            raise NotExistingMessageError(str(id_message) + " message not found")
        else:
            return message

    @staticmethod
    def add_draft(msg: Message) -> None:
        db.session.add(msg)
        db.session.commit()

    @staticmethod
    def update_draft(id: int, body_message: str, date_of_send: datetime):
        db.session.query(Message).filter(Message.id_message == id).update(
            {Message.body_message: body_message, Message.date_of_send: date_of_send}
        )
        db.session.commit()

    @staticmethod
    def send_message(id_message):
        db.session.query(Message).filter(Message.id_message == id_message).update(
            {Message.is_sent: 1}
        )
        db.session.commit()

    @staticmethod
    def arrived_message():
        messages = db.session.query(Message).filter(
            Message.is_sent == True,
            Message.is_arrived == False,
            Message.date_of_send is not None,
        )

        messages_arrived = []
        
        for m in messages.all():
            if (m.date_of_send - datetime.now()).total_seconds() <= 0:

                m.is_arrived = True
                messages_arrived.append(m)

        db.session.commit()
        
        return [
            {
                "id": m.id_message,
                "date": m.date_of_send.strftime("%H:%M %d/%m/%Y"),
                "sent": m.is_sent,
                "received": m.is_arrived,
                "notified": [
                    (rcp.id_recipient, rcp.is_notified) for rcp in m.recipients
                ],
            }
            for m in messages_arrived
        ]
      
    @staticmethod
    def get_notify_recipient(id):
        notify_list = (
            db.session.query(Recipient)
            .filter(Recipient.is_notified == False, Recipient.id_recipient == id)
            .filter(
                Recipient.message.has(
                    and_(Message.is_arrived == True, Message.is_sent == True)
                )
            )
            .all()
        )

        for notify in notify_list: 
            notify.is_notified = True

        db.session.commit()

        return notify_list

    @staticmethod
    def get_notify_sender(id):

        notifies = db.session.query(Message)\
                                     .filter(id == Message.id_sender,\
                                             Message.is_notified_sender == False,\
                                             Message.is_arrived == True, \
                                             Message.is_sent == True)

        notify_list = []
        for notify in notifies.all():
            notify.is_notified_sender = True
            notify_list.append(notify)

        db.session.commit()

        return [{'id_message' : notify.id_message,\
                'date' : notify.date_of_send.strftime("%H:%M %d/%m/%Y"),\
                'id_sender' : notify.id_sender,\
                'id_receipent' : notify.id_receipent} for notify in notify_list]



    @staticmethod
    def create_message(
        id_sender: int,
        body_message: str,
        recipients: List[int] = [],
        date_of_send: datetime = datetime.now(),
        is_sent = False,
        is_arrived = False,
        is_notified = False,
        reply_to = None,
        to_filter = False
    ):
        message = Message()
        message.id_sender = id_sender
        message.body_message = body_message
        message.date_of_send = date_of_send
        message.is_sent = is_sent
        message.is_arrived = is_arrived
        message.is_notified = is_notified
        message.reply_to = reply_to
        message.to_filter = to_filter

        db.session.add(message)
        db.session.flush()

        _recipients = []
        for rcp in recipients:
            if rcp not in _recipients:
                _recipients.append(rcp)
        message.recipients = [
            Recipient(id_recipient=recipient_id) for recipient_id in _recipients
        ]

        db.session.commit()

        return message

    @staticmethod
    def delete_message(id_message: int):
        mess = MessageModel.id_message_exists(id_message)

        # needed to clean up the Recipient table in the db
        mess.recipients = []

        db.session.delete(mess)
        db.session.commit()

    @staticmethod
    def user_can_read(user_id: int, message: Message) -> bool:
        recipients = [rcp.id_recipient for rcp in message.recipients]
        if message.is_arrived == True:
            if user_id not in recipients and user_id != message.id_sender:
                return False
        elif user_id != message.id_sender:
            return False

        return True

    @staticmethod
    def user_can_reply(user_id: int, message: Message) -> bool:
        recipients = [rcp.id_recipient for rcp in message.recipients]
        return message.is_arrived == True and user_id in recipients

    @staticmethod
    def get_replying_info(reply_to: Optional[int]) -> Optional[dict]:
        try:
            if reply_to is None:
                raise NotExistingMessageError('Trying to reply to a non existing message')

            r_message = MessageModel.id_message_exists(reply_to) if reply_to else None
            r_user = db.session.query(User).filter(User.id == r_message.id_sender).first() 
            return {
                'message': r_message,
                'user': r_user,
            } if r_user else None
        except NotExistingMessageError:
            return None


class NotExistingMessageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

