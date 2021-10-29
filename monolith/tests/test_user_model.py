import sqlalchemy
import datetime
from monolith.database import db, User
from monolith.classes.user import UserModel, NotExistingUser
import pytest


class TestUserModel:

    def test_create_user(self,test_user,session):
        user = UserModel.create_user(test_user, password="pass")
        assert user is not None
        assert user.email == "fake@fake.com"
        assert user.authenticate("pass")
        session.query(User).filter_by(email=user.email).delete()
        session.commit()

    def test_create_user_not_unique_email(self,test_user,session):
        
        user = UserModel.create_user(test_user, password="pass")
        assert user is not None
        user2 = User(
            firstname="Niccolò",
            lastname="Piazzesi",
            email="fake@fake.com",
            dateofbirth=datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")
        )
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            user2 = UserModel.create_user(user2, password="pass")
        session.rollback()
        session.query(User).filter_by(email=user.email).delete()
        session.commit()

    def test_get_user_from_mail_exists(self):
        user = UserModel.get_user_info_by_email("example@example.com")
        assert user is not None
        assert user.email == "example@example.com"

    def test_get_user_from_mail_not_exists(self):
        with pytest.raises(NotExistingUser)as ex:
            UserModel.get_user_info_by_email("fail@fail.com")
        assert str(ex.value) == "No user with email fail@fail.com was found"
    
    def test_get_user_from_id_exists(self):
        user = UserModel.get_user_info_by_id(1)
        assert user is not None
        assert user.email == "example@example.com"

    def test_get_user_from_id_not_exists(self):
        with pytest.raises(NotExistingUser) as ex:
            UserModel.get_user_info_by_id(999)
        assert str(ex.value) == "No user found!"

    def test_delete_user_by_id_ok(self, test_user):
       
        UserModel.create_user(test_user, password='p')
        rows = UserModel.delete_user(id=2)
        assert rows == 1

    def test_delete_user_by_mail_ok(self,test_user):
      
        user = UserModel.create_user(test_user, password='p')

        rows = UserModel.delete_user(email="fake@fake.com")
        assert rows == 1

    def test_delete_user_by_id_not_exists(self):
        with pytest.raises(NotExistingUser) as ex:
            UserModel.delete_user(id=999)
            
        assert str(ex.value) == "No user found!"

    def test_delete_user_by_email_not_exists(self):
        with pytest.raises(NotExistingUser) as ex:
            UserModel.delete_user(email="nomail@fail.com")
        assert str(ex.value) == "No user found!"
    
    def test_get_users_ok(self):
        users = UserModel.get_user_list()
        assert len(users) == 1 