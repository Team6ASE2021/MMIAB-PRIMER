from http import HTTPStatus

import pytest
from flask import get_flashed_messages

from monolith.database import db
from monolith.database import User


@pytest.mark.usefixtures("clean_db_and_logout")
class TestViewsAuth:
    def test_login_user_exists(self, test_client):

        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Logout" in response.data
        test_client.get("/logout", follow_redirects=True)

    def test_login_user_form_not_submitted(self, test_client):
        response = test_client.get("/login")
        assert response.status_code == 200
        assert b"submit" in response.data

    def test_login_user_not_exists(self, test_client):
        response = test_client.post(
            "/login",
            data={"email": "bla@bla.com", "password": "adfv"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Logout" not in response.data

    def test_login_user_banned(self, test_client):
        usr = db.session.query(User).first()
        usr.is_banned = True
        db.session.commit()
        response = test_client.post(
            "/login",
            data={"email": usr.email, "password": "admin"},
            follow_redirects=True,
        )
        assert response.status_code == HTTPStatus.OK
        assert "You are banned!" in get_flashed_messages()
        usr.is_banned = False
        db.session.commit()

    def test_login_wrong_password(self, test_client):
        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "af"},
            follow_redirects=True,
        )
        assert response.status_code == HTTPStatus.OK
        assert "Wrong password" in get_flashed_messages()
        test_client.get("/logout", follow_redirects=True)
