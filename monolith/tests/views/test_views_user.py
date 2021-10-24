class TestViewsUser:

#TODO: refactor to generate test data automatically

     def test_users_list(self, test_client):
        response = test_client.get('/users')
        assert response.status_code == 200
        assert b'User List' in response.data

     
     def test_show_create_user_form(self, test_client):
          response = test_client.get("/create_user")
          assert response.status_code == 200
          assert b'submit' in response.data
    
     def test_create_user_ok(self, test_client):
        data = {
            'firstname': 'Niccolò',
            'lastname': 'Piazzesi',
            'email': 'abc@abc.com',
            'password': 'abc',
            'dateofbirth': '01/01/2000'
        }
        response = test_client.post('/create_user', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Hi' in response.data
        test_client.get('/logout')

     def test_show_user_info(self, test_client):
        response = test_client.post("/login", data={'email': 'example@example.com',
                                    'password': 'admin'}, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.get("/user/info")
        assert response.status_code == 200
        assert b'User info' in response.data
        test_client.get("/logout")