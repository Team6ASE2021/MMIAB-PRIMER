import pytest


@pytest.mark.usefixtures("clean_db_and_logout", "messages_setup")
class TestViewsForward:
    def test_forward_mess_not_auth(self, test_client):
        test_client.get("/logout")
        response = test_client.get("/forwarding/1", follow_redirects=True)
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_forward_mess_auth(self, test_client):
        test_client.get("/logout", follow_redirects=True)
        admin_user = {"email": "example@example.com", "password": "admin"}
        response = test_client.post("/login", data=admin_user, follow_redirects=True)
        assert response.status_code == 200

        response = test_client.get("/forwarding/1", follow_redirects=True)
        assert response.status_code == 200
