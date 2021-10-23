from monolith.views import home
class TestHome:

    def test_home_page_show_anonymous(self, test_client):
        response = test_client.get('/')
        assert b"<h1>My Message in a Bottle -- Primer</h1>" in response.data
        assert b" Hi Anonymous" in response.data

    def test_home_page_user_logged_in(self, test_client):
        assert False
    
