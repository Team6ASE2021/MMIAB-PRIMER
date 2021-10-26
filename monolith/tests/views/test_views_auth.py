class TestViewsAuth:
    
    def test_login_user_exists(self, test_client):
        
        response = test_client.post("/login", data={'email':'example@example.com', 'password':'admin'},follow_redirects=True)
        assert response.status_code == 200
        assert b"Hi" in response.data
        test_client.get('/logout',follow_redirects=True)
    
    def test_login_user_form_not_submitted(self,test_client):
        response = test_client.get("/login")
        assert response.status_code == 200
        assert b'submit' in response.data

    def test_login_user_not_exists(self,test_client):
        response = test_client.post('/login', data={'email':'bla@bla.com','password':'adfv'},follow_redirects=True)
        assert response.status_code == 200       
        assert b"Hi" not in response.data


        
