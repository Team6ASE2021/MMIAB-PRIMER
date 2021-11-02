import datetime
import string
from os import path
from typing import Optional

from monolith.database import db
from monolith.database import Message
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


# list of alpha-numeric characters


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
    def update_draft(id: int, msg: Message):
        db.session.query(Message).filter_by(id_message=id).update(
            {
                Message.id_receipent: msg.id_receipent,
                Message.body_message: msg.body_message,
                Message.date_of_send: msg.date_of_send,
            }
        )
        db.session.commit()

    @staticmethod
    def send_message(id_message):
        db.session.query(Message).filter(Message.id_message == id_message).update(
            {Message.is_sended: 1}
        )
        db.session.commit()

    @staticmethod
    def arrived_message():

        messages = db.session.query(Message).filter(
            Message.is_sended == True,
            Message.is_arrived == False,
            Message.date_of_send is not None,
        )

        messages_arrived = []
        for m in messages:
            if (m.date_of_send - datetime.datetime.now()).total_seconds() <= 0:
                m.is_arrived = True
                messages_arrived.append(m)

        db.session.commit()

        # return messages_arrived
        return [
            {
                "id": m.id_message,
                "date": m.date_of_send.strftime("%H:%M %d/%m/%Y"),
                "sent": m.is_sended,
                "received": m.is_arrived,
                "notified": m.is_notified,
            }
            for m in messages_arrived
        ]

    @staticmethod
    def get_notify(user: User):
        notify_list = db.session.query(Message).filter(
            user.id == Message.id_receipent,
            Message.is_notified == False,
            Message.is_arrived == True,
            Message.is_sended == True,
        )

        for notify in notify_list:
            notify.is_notified = True

        db.session.commit()

        return notify_list

    @staticmethod
    def create_message(
        id_sender=1,
        id_receipent=1,
        body_message="",
        date_of_send=None,
        is_sended=False,
        is_arrived=False,
    ):
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

    @staticmethod
    def delete_message(id_message: int):
        mess = MessageModel.id_message_exists(id_message)
        db.session.delete(mess)
        db.session.commit()


class NotExistingMessageError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
