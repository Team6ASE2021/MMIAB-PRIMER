import pytest

from monolith.classes.notify import NotifyModel
from monolith.database import db, Notify

@pytest.mark.usefixtures("clean_db_and_logout")
class TestNotify:

    def test_add_notify(self):
        NotifyModel.add_notify(id_user=1, id_message=1, for_sender=True, \
                               for_recipient=False, for_lottery=False, from_recipient=None)

        notify = db.session.query(Notify).filter(Notify.id_user == 1).first()
        assert notify.id_message == 1
        assert notify.for_sender == True

    def test_get_notify(self):
        NotifyModel.add_notify(id_user=1, id_message=1, for_sender=True, \
                               for_recipient=False, for_lottery=False, from_recipient=None)

        notify = NotifyModel.get_notify(id_user=1)
        assert notify[1]["is_notified"] == True
        assert notify[1]["for_sender"] == True
 
    def test_to_notify(self):
        assert NotifyModel.to_notify(id_sender=1, id_recipient=2, id_message=1) == True

    def test_not_to_notify(self):
        NotifyModel.add_notify(id_user=1, id_message=1, for_sender=True, \
                               for_recipient=False, for_lottery=False, from_recipient=2)

        assert NotifyModel.to_notify(id_sender=1, id_recipient=2, id_message=1) == False