from monolith.database import Notify, db, User, Message, Report
import datetime

class NotifyModel:
    """
        Wrapper class  for all db operations involving notify
    """
    
    def add_notify(id_message, id_user, for_recipient, for_sender, for_lottery, from_recipient):
        
        db.session\
            .add(Notify(id_message=id_message, id_user=id_user, \
                        for_recipient=for_recipient, for_lottery=for_lottery, for_sender=for_sender, from_recipient=from_recipient))
        db.session.commit()

    def get_notify(id_user):
        notifies = db.session.query(Notify).filter(Notify.id_user==id_user, Notify.is_notified==False).all()

        notify_list = []
        for notify in notifies:
            notify.is_notified = True
            notify_list.append(notify)
        db.session.commit()

        return [
            {
                "id_user": notify.id_user,
                "id_message" : notify.id_message,
                "is_notified": notify.is_notified,
                "from_receipent": notify.from_recipient,
                "for_sender" : notify.for_sender,
                "for_recipient" : notify.for_recipient,
                "for_lottery" : notify.for_lottery,
            }
            for notify in notify_list]

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