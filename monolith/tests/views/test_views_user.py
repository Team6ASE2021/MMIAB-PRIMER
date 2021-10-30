from http import HTTPStatus
from monolith.app import db
from monolith.database import User
from monolith.classes.user import UserModel  

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
        assert response.status_code == HTTPStatus.OK
        assert b'Login' in response.data
        response = test_client.get('/users/2/delete',follow_redirects=True)
        assert response.status_code == HTTPStatus.OK
        assert b'Anonymous' in response.data

    def test_show_user_info(self, test_client):
        response = test_client.post("/login", data={'email': 'example@example.com', 
                                    'password': 'admin'}, follow_redirects=True)
        assert response.status_code == 200
        response = test_client.get(f"/users/{1}")
        assert response.status_code == 200
        assert b'User info' in response.data
        test_client.get("/logout")

    def test_user_list_logged(self, test_client):
        #do the login
        response = test_client.post("/login", data={'email': 'example@example.com',
                                'password': 'admin'}, follow_redirects=True)
        assert response.status_code == 200

        #do the user_list request
        response = test_client.get('/user_list')
        assert b'User list'
        test_client.get('/logout')


    def test_user_list_not_logged(self, test_client):
        test_client.get('/logout')
        response = test_client.get('/user_list')

        assert response.status_code == 401

    def test_user_content_filter_not_logged(self, test_client):
        test_client.get('/logout')
        response = test_client.get('/user/content_filter')

        assert response.status_code == 401

    def test_user_content_filter_set_unset(self, test_client):
        admin_user = {'email': 'example@example.com', 'password': 'admin'}
        test_client.post('/login', data=admin_user, follow_redirects=True)

        admin_db = db.session.query(User).filter(User.email = admin_user['email']).first()
        assert admin_db.content_filter == False

        response = test_client.get('/user/content_filter', follow_redirects = True)
        assert response.status_code == 200
        assert admin_db.content_filter == True

        response = test_client.get('/user/content_filter', follow_redirects = True)
        assert response.status_code == 200
        assert admin_db.content_filter == False




