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

        notify = db.session.query(Notify).filter(Notify.id_user == 1).first()
        assert notify.for_sender == True
        assert notify.id_message == 1
        db.session.delete(notify)
        db.session.commit()

    def test_get_notify(self):
        db.session.add(Notify(
            id_message=1,
            id_user=1,
            for_sender=True,
            from_recipient=1
        ))
        db.session.add(Notify(
            id_message=1,
            id_user=1,
            for_recipient=True,
        ))
        db.session.commit()

        notify = NotifyModel.get_notify(id_user=1)
        assert notify['sender_notify'][0]['is_notified'] == True
        assert notify['sender_notify'][0]["for_sender"] == True
        assert notify['sender_notify'][0]["from_recipient"] == 'Admin Admin'

        assert notify['recipient_notify'][0]["is_notified"] == True
        assert notify['recipient_notify'][0]["for_recipient"] == True
