import pytest

from monolith.auth import current_user
from monolith.database import db
from monolith.database import Message
from monolith.database import Recipient


@pytest.mark.usefixtures("clean_db_and_logout", "messages_setup")
class TestViewsMailbox:
    def test_mailbox_not_logged(self, test_client):
        response = test_client.get("/message/list/received", follow_redirects=True)
        assert response.status_code == 200
        assert b"Login" in response.data

        response = test_client.get("/message/list/sent", follow_redirects=True)
        assert response.status_code == 200
        assert b"Login" in response.data

        response = test_client.get("/message/list/draft", follow_redirects=True)
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_mailbox_count(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        response = test_client.post("/login", data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        db_count = (
            db.session.query(Message)
            .filter(Message.is_arrived == True)
            .filter(Message.recipients.any(Recipient.id_recipient == current_user.id))
            .count()
        )
        response = test_client.get("/message/list/received")
        assert response.status_code == 200
        assert (
            response.data.count(b'<div class="row bg-info mb-2 rounded-3 message-row"')
            == db_count
        )

        db_count = (
            db.session.query(Message)
            .filter(Message.id_sender == current_user.id, Message.is_sent == True)
            .count()
        )
        response = test_client.get("/message/list/sent")
        assert response.status_code == 200
        assert (
            response.data.count(b'<div class="row bg-info mb-2 rounded-3 message-row"')
            == db_count
        )

        db_count = (
            db.session.query(Message)
            .filter(Message.id_sender == current_user.id, Message.is_sent == False)
            .count()
        )
        response = test_client.get("/message/list/draft")
        assert response.status_code == 200
        assert (
            response.data.count(b'<div class="row bg-info mb-2 rounded-3 message-row"')
            == db_count
        )
