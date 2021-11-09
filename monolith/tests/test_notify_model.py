import pytest

from monolith.classes.notify import NotifyModel
from monolith.database import db, Notify

@pytest.mark.usefixtures("clean_db_and_logout")
class TestNotify:

    def test_add_notify(self):
        NotifyModel.add_notify(
            id_message=1, 
            id_user=1, 
            for_sender=True,
       )

        print(db.session.query(Notify).count())
        notify = db.session.query(Notify).filter(Notify.id_user == 1).first()
        print(notify.id_message, notify.id_user)
        assert notify.for_sender == True
        assert notify.id_message == 1
        db.session.delete(notify)

    def test_get_notify(self):
        NotifyModel.add_notify(
            id_user=1, 
            id_message=1, 
            for_sender=True,
            from_recipient=1,
        )

        notify = NotifyModel.get_notify(id_user=1)
        assert notify['sender_notify'][0]["is_notified"] == True
        assert notify['sender_notify'][0]["for_sender"] == True
        assert notify['sender_notify'][0]["from_recipient"] == 'Admin Admin'
        db.session.query(Notify).filter(Notify.id_user == 1).delete()
 
        NotifyModel.add_notify(
            id_user=2, 
            id_message=1, 
            for_recipient=True,
        )

        notify = NotifyModel.get_notify(id_user=2)
        assert notify['recipient_notify'][0]["is_notified"] == True
        assert notify['recipient_notify'][0]["for_recipient"] == True
        db.session.query(Notify).filter(Notify.id_user == 2).delete()

        NotifyModel.add_notify(
            id_user=3, 
            id_message=1, 
            for_lottery=True,
        )

        notify = NotifyModel.get_notify(id_user=3)
        assert notify['lottery_notify'][0]["is_notified"] == True
        assert notify['lottery_notify'][0]["for_lottery"] == True
        db.session.query(Notify).filter(Notify.id_user == 3).delete()
        assert db.session.query(Notify).count() == 0
