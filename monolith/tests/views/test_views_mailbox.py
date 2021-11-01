from datetime import datetime

import pytest
from flask_login import logout_user

from monolith import app
from monolith.auth import current_user
from monolith.database import db
from monolith.database import Message
from monolith.database import User
from monolith.forms import delivery_format


@pytest.mark.usefixtures("messages_setup", "clean_db_and_logout")
class TestViewsMailbox:
    def test_mailbox_not_logged(self, test_client):
        response = test_client.get("/message/list/received")
        assert response.status_code == 200
        assert b"Hi Anonymous" in response.data

        response = test_client.get("/message/list/sent")
        assert response.status_code == 200
        assert b"Hi Anonymous" in response.data

        response = test_client.get("/message/list/draft")
        assert response.status_code == 200
        assert b"Hi Anonymous" in response.data

    def test_mailbox_count(self, test_client):
        admin_user = {"email": "example@example.com", "password": "admin"}
        response = test_client.post("/login", data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        db_count = (
            db.session.query(Message)
            .filter(
                Message.id_receipent == current_user.id and Message.is_arrived == True
            )
            .count()
        )
        response = test_client.get("/message/list/received")
        assert response.status_code == 200
        assert response.data.count(b'div class="message-block"') == db_count

        db_count = (
            db.session.query(Message)
            .filter(Message.id_sender == current_user.id and Message.is_sended == True)
            .count()
        )
        response = test_client.get("/message/list/sent")
        assert response.status_code == 200
        assert response.data.count(b'div class="message-block"') == db_count

        db_count = (
            db.session.query(Message)
            .filter(Message.id_sender == current_user.id and Message.is_sended == False)
            .count()
        )
        response = test_client.get("/message/list/draft")
        assert response.status_code == 200
        assert response.data.count(b'div class="message-block"') == db_count
