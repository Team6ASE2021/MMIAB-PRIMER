

class TestViewsHome:

    def test_home_page_show_anonymous(self, test_client):
        
        response = test_client.get('/')
        assert b"<h1>My Message in a Bottle -- Primer</h1>" in response.data
        assert b" Hi Anonymous" in response.data
    
    def test_home_page_user_logged_in(self, test_client):
        response = test_client.post("/login", data={'email':'example@example.com', 'password':'admin'},follow_redirects=True)
        response = test_client.get('/')
        assert response.status_code == 200
        assert b"Logged In!" in response.data
        test_client.get('/logout')
