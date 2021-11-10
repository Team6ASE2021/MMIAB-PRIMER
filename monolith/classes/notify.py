from typing import Optional

from monolith.classes.user import UserModel
from monolith.database import db
from monolith.database import Notify


class NotifyModel:
    """
    Wrapper class  for all db operations involving notify
    """

    def add_notify(
        id_user: int,
        id_message: Optional[int] = None,
        for_recipient: bool = False,
        for_sender: bool = False,
        for_lottery: bool = False,
        from_recipient: Optional[int] = None,
    ):

        db.session.add(
            Notify(
                id_message=id_message,
                id_user=id_user,
                for_recipient=for_recipient,
                for_lottery=for_lottery,
                for_sender=for_sender,
                from_recipient=from_recipient,
            )
        )
        db.session.commit()

    def get_notify(id_user):
        """
        Returns a dictionary contaning three lists of notifications for the specified user,
        one for each kind.
        """
        notifies = (
            db.session.query(Notify)
            .filter(Notify.id_user == id_user, Notify.is_notified == False)
            .all()
        )

        notify_list = []
        for notify in notifies:
            notify.is_notified = True
            notify_list.append(notify)
        db.session.commit()

        sender_notify = list(filter(lambda n: n.for_sender == True, notify_list))

        from_recipients = UserModel.get_users_by_ids(
            [n.from_recipient for n in sender_notify]
        )
        recipients_dict = {
            user.id: (user.firstname + " " + user.lastname) for user in from_recipients
        }

        recipient_notify = list(filter(lambda n: n.for_recipient == True, notify_list))
        lottery_notify = list(filter(lambda n: n.for_lottery == True, notify_list))

        map_dictionary = lambda n: {
            "id_user": n.id_user,
            "id_message": n.id_message,
            "is_notified": n.is_notified,
            "from_recipient": recipients_dict.get(n.from_recipient, "Anonymous")
            if n.from_recipient is not None
            else "Anonymous",
            "for_sender": n.for_sender,
            "for_recipient": n.for_recipient,
            "for_lottery": n.for_lottery,
        }

        sender_notify = list(map(map_dictionary, sender_notify))
        recipient_notify = list(map(map_dictionary, recipient_notify))
        lottery_notify = list(map(map_dictionary, lottery_notify))

        return {
            "sender_notify": sender_notify,
            "recipient_notify": recipient_notify,
            "lottery_notify": lottery_notify,
        }

