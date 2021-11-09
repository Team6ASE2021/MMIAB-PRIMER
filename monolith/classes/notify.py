from monolith.database import Notify, db, User, Message, Report
import datetime
from typing import Optional

class NotifyModel:
    """
        Wrapper class  for all db operations involving notify
    """
    
    def add_notify(
            id_message: int, 
            id_user: int, 
            for_recipient: bool = False, 
            for_sender: bool = False, 
            for_lottery: bool = False, 
            from_recipient: Optional[int] = None
        ):
        
        db.session.add(
            Notify(
                id_message=id_message, 
                id_user=id_user,
                for_recipient=for_recipient, 
                for_lottery=for_lottery, 
                for_sender=for_sender, 
                from_recipient=from_recipient
            )
        )
        db.session.commit()

    def get_notify(id_user):
        notifies = (
            db.session.query(Notify)
            .filter(
                Notify.id_user==id_user, 
                Notify.is_notified==False
            )
            .all()
        )

        notify_list = []
        for notify in notifies:
            notify.is_notified = True
            notify_list.append(notify)
        db.session.commit()

        sender_notify = list(filter(lambda n: n.for_sender == True, notify_list))
        recipient_notify = list(filter(lambda n: n.for_recipient == True, notify_list))
        lottery_notify = list(filter(lambda n: n.for_lottery == True, notify_list))

        map_dictionary = lambda n: {
            "id_user": n.id_user,
            "id_message" : n.id_message,
            "is_notified": n.is_notified,
            "from_receipent": n.from_recipient,
            "for_sender" : n.for_sender,
            "for_recipient" : n.for_recipient,
            "for_lottery" : n.for_lottery,
        }

        sender_notify = list(map(map_dictionary, sender_notify))
        recipient_notify = list(map(map_dictionary, recipient_notify))
        lottery_notify = list(map(map_dictionary, lottery_notify))

        return {
            'sender_notify': sender_notify,
            'recipient_notify': recipient_notify,
            'lottery_notify': lottery_notify
        }

    """
    def to_notify(id_sender, id_recipient, id_message):
        count = db.session\
                .query(Notify)\
                .filter(Notify.id_user == id_sender, \
                        Notify.for_sender == True, \
                        Notify.id_message == id_message, \
                        Notify.from_recipient == id_recipient)\
                .count()

        if count == 0:
            return True
        else:
            return False
    """
    def to_notify(id_sender, id_recipient, id_message):
