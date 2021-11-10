from http import HTTPStatus

import pytest
from flask import url_for


@pytest.mark.usefixtures("clean_db_and_logout", "lottery_setup")
class TestViewsLotteryParticipate:
    def test_participate_not_logged(self, test_client):
        response = test_client.get(
            url_for("lottery.participate"), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"Login" in response.data

    def test_participate_already_played(self, test_client):
        user = {"email": "test@test.com", "password": "test"}
        test_client.post("/login", data=user)
        response = test_client.get(
            url_for("lottery.participate"), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"The next lottery will be" in response.data
        assert b"3" in response.data

    def test_get_participate_form(self, test_client):
        user = {"email": "example@example.com", "password": "admin"}
        test_client.post(url_for("auth.login"), data=user)
        response = test_client.get(
            url_for("lottery.participate"), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"Choose a number between 1 and 50" in response.data
        assert b"Participate" in response.data

    def test_participate_choice_out_of_range(self, test_client):
        user = {"email": "example@example.com", "password": "admin"}
        test_client.post(url_for("auth.login"), data=user)
        data = {"choice": 51}
        response = test_client.post(
            url_for("lottery.participate"), data=data, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"between 1 and 50" in response.data
        assert b"Participate" in response.data
        data = {"choice": 0}
        response = test_client.post(
            url_for("lottery.participate"), data=data, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"between 1 and 50" in response.data

    def test_participate_choice_ok(self, test_client):
        user = {"email": "example@example.com", "password": "admin"}
        test_client.post(url_for("auth.login"), data=user)
        data = {"choice": 50}
        response = test_client.post(
            url_for("lottery.participate"), data=data, follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"The next lottery" in response.data
        assert b"50" in response.data


@pytest.mark.usefixtures("clean_db_and_logout", "lottery_setup")
class TestViewsSeeLottery:
    def test_participate_not_logged(self, test_client):
        response = test_client.get(
            url_for("lottery.next_lottery"), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"Login" in response.data

    def test_see_lottery_not_participant(self, test_client):
        user = {"email": "example@example.com", "password": "admin"}
        test_client.post(url_for("auth.login"), data=user)
        response = test_client.get(
            url_for("lottery.next_lottery"), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"The next lottery will be" in response.data
        assert b"Participate" in response.data

    def test_see_lottery_already_participant(self, test_client):
        user = {"email": "test@test.com", "password": "test"}
        test_client.post(url_for("auth.login"), data=user)
        response = test_client.get(
            url_for("lottery.next_lottery"), follow_redirects=True
        )
        assert response.status_code == HTTPStatus.OK
        assert b"The next lottery will be" in response.data
        assert b"3" in response.data
