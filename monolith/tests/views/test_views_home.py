class TestViewsHome:
    def test_home_page_show_anonymous(self, test_client):

        response = test_client.get("/")
        assert b"mmiab" in response.data
        assert b"Login" in response.data

    def test_home_page_user_logged_in(self, test_client):
        response = test_client.post(
            "/login",
            data={"email": "example@example.com", "password": "admin"},
            follow_redirects=True,
        )
        response = test_client.get("/", follow_redirects=True)
        assert response.status_code == 200
        print(response.data)
        assert b"Mailbox" in response.data
        test_client.get("/logout")
