from http import HTTPStatus
from monolith.app import db
from monolith.database import User
from monolith.classes.user import UserModel  
class TestViewsUser:

#TODO: refactor to generate test data automatically

   def test_users_list(self, test_client):
      response = test_client.get('/users')
      assert response.status_code == HTTPStatus.OK
      assert b'User List' in response.data

   
   def test_show_create_user_form(self, test_client):
         response = test_client.get("/create_user")
         assert response.status_code == HTTPStatus.OK
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
      assert b'Hi' in response.data
      test_client.get('/logout')
      UserModel.delete_user(email=data['email'])
      
   def test_show_user_info(self, test_client):
      response = test_client.post("/login", data={'email': 'example@example.com',
                                 'password': 'admin'}, follow_redirects=True)
      assert response.status_code == HTTPStatus.OK
      response = test_client.get(f"/users/{1}")
      assert response.status_code == HTTPStatus.OK
      assert b'User info' in response.data
      assert b'Admin' in response.data
      test_client.get("/logout")

   def test_delete_account_ok(self, test_client):
      data = {
            'firstname': 'Niccolò',
            'lastname': 'Piazzesi',
            'email': 'abc@abc.com',
            'password': 'abc',
            'dateofbirth': '01/01/2000'
         }
      response = test_client.post('/create_user', data=data, follow_redirects=True)
      assert response.status_code == HTTPStatus.OK
      assert b'Hi' in response.data
      response = test_client.get('/users/2/delete',follow_redirects=True)
      assert response.status_code == HTTPStatus.OK
      assert b'Anonymous' in response.data

